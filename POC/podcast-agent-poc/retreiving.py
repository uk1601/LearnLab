import os
from getpass import getpass
from semantic_router.encoders import OpenAIEncoder
from semantic_router.splitters import RollingWindowSplitter
from semantic_router.utils.logger import logger
from semantic_router.schema import DocumentSplit
import PyPDF2
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
import time
from tqdm.auto import tqdm
from dotenv import load_dotenv
import hashlib

load_dotenv()

class PDFProcessor:
    def __init__(self, openai_api_key: str, pinecone_api_key: str):
        """Initialize the PDF processor with necessary components."""
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.encoder = OpenAIEncoder(name="text-embedding-3-small")
        logger.setLevel("WARNING")
        
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.dims = len(self.encoder(["test"])[0])
        
        self.splitter = RollingWindowSplitter(
            encoder=self.encoder,
            dynamic_threshold=True,
            min_split_tokens=100,
            max_split_tokens=500,
            window_size=2,
            plot_splits=True,
            enable_statistics=True
        )
        
        self.index = None

    def create_index(self, index_name: str = "pdf-embeddings-semantic"):
        """Create and initialize Pinecone index."""
        # Setup serverless specification
        spec = ServerlessSpec(cloud="aws", region="us-east-1")
        
        # Create index if it doesn't exist
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=self.dims,
                metric='dotproduct',
                spec=spec
            )
            # Wait for index to be initialized
            while not self.pc.describe_index(index_name).status['ready']:
                time.sleep(1)
        
        # Connect to index
        self.index = self.pc.Index(index_name)
        time.sleep(1)
        return self.index.describe_index_stats()
    
    def build_chunk(self, title: str, content: str) -> str:
        """Format chunk with title for embedding."""
        return f"# {title}\n{content}"

    def calculate_document_hash(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Calculate a unique hash for a document based on its content and relevant metadata.
        """
        hash_input = f"{content}{metadata.get('title', '')}{metadata.get('processed_date', '')}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def check_document_exists(self, doc_hash: str) -> Tuple[bool, List[str]]:
        """
        Check if a document with the same hash exists in the index.
        Returns a tuple of (exists: bool, chunk_ids: List[str]).
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")

        # Query the index for chunks with matching document hash
        query_response = self.index.query(
            vector=[0] * self.dims,  # Dummy vector for metadata-only query
            top_k=1,
            filter={"doc_hash": doc_hash},
            include_metadata=True
        )

        exists = len(query_response.matches) > 0
        
        if exists:
            # Fetch all chunk IDs for this document
            fetch_response = self.index.query(
                vector=[0] * self.dims,
                top_k=10000,  # Large number to get all chunks
                filter={"doc_hash": doc_hash},
                include_metadata=True
            )
            chunk_ids = [match.id for match in fetch_response.matches]
            return True, chunk_ids
        
        return False, []

    def delete_document_chunks(self, chunk_ids: List[str]) -> bool:
        """
        Delete specific chunks from the index.
        """
        try:
            if chunk_ids:
                self.index.delete(ids=chunk_ids)
            return True
        except Exception as e:
            print(f"Error deleting chunks: {str(e)}")
            return False

    def build_metadata(self, doc: Dict[str, Any], doc_splits: List[DocumentSplit]) -> List[Dict[str, Any]]:
        """Create metadata for each chunk including contextual information."""
        metadata = []
        for i, split in enumerate(doc_splits):
            chunk_id = f"{doc['doc_id']}#{i}"
            prechunk_id = "" if i == 0 else f"{doc['doc_id']}#{i-1}"
            postchunk_id = "" if i+1 == len(doc_splits) else f"{doc['doc_id']}#{i+1}"
            
            metadata.append({
                "id": chunk_id,
                "title": doc["title"],
                "content": split.content,
                "prechunk_id": prechunk_id,
                "postchunk_id": postchunk_id,
                "doc_id": doc["doc_id"],
                "pages": doc["pages"],
                "processed_date": doc["processed_date"],
                "references": doc["references"]
            })
        return metadata

    def index_document(self, doc_info: Dict[str, Any], batch_size: int = 128, overwrite: bool = False) -> Tuple[int, bool]:
        """
        Index document chunks in Pinecone with validation and overwrite control.
        Returns tuple of (number of chunks indexed, whether document was overwritten).
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")

        # Calculate document hash
        doc_hash = self.calculate_document_hash(doc_info["content"], doc_info)
        
        # Check if document already exists
        exists, existing_chunks = self.check_document_exists(doc_hash)
        
        if exists:
            if not overwrite:
                print(f"Document '{doc_info['title']}' already exists in the index.")
                return 0, False
            
            # Delete existing chunks if overwriting
            print(f"Overwriting existing document '{doc_info['title']}'...")
            if not self.delete_document_chunks(existing_chunks):
                raise Exception("Failed to delete existing document chunks")
        
        # Create splits
        splits = self.splitter([doc_info["content"]])
        
        # Create metadata for all splits
        metadata = self.build_metadata(doc=doc_info, doc_splits=splits)
        
        # Add document hash to metadata
        for m in metadata:
            m["doc_hash"] = doc_hash
        
        # Process in batches
        for i in range(0, len(splits), batch_size):
            i_end = min(len(splits), i+batch_size)
            metadata_batch = metadata[i:i_end]
            
            # Generate IDs and content for embedding
            ids = [m["id"] for m in metadata_batch]
            content = [
                self.build_chunk(title=x["title"], content=x["content"]) 
                for x in metadata_batch
            ]
            
            # Create embeddings
            embeds = self.encoder(content)
            
            # Upload to Pinecone
            self.index.upsert(vectors=zip(ids, embeds, metadata_batch))
            
        return len(splits), exists

    def read_pdf(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Read PDF and extract content with metadata."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                doc_info = {
                    "file_path": file_path,
                    "title": os.path.splitext(os.path.basename(file_path))[0],
                    "pages": len(pdf_reader.pages),
                    "content": text,
                    "processed_date": datetime.now().isoformat(),
                    "doc_id": f"doc_{hash(file_path)}",
                    "references": []
                }
                return doc_info
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return None

    def query(self, text: str, top_k: int = 3) -> List[str]:
        """Query the index for similar chunks."""
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
            
        # Create query embedding
        xq = self.encoder([text])[0]
        
        # Query index
        matches = self.index.query(
            vector=xq,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        chunks = []
        for m in matches["matches"]:
            content = m["metadata"]["content"]
            title = m["metadata"]["title"]
            pre_id = m["metadata"]["prechunk_id"]
            post_id = m["metadata"]["postchunk_id"]
            
            # Fetch surrounding chunks if they exist
            context = ""
            if pre_id or post_id:
                ids_to_fetch = [id for id in [pre_id, post_id] if id]
                if ids_to_fetch:
                    other_chunks = self.index.fetch(ids=ids_to_fetch)["vectors"]
                    
                    if pre_id and pre_id in other_chunks:
                        context += other_chunks[pre_id]["metadata"]["content"][-400:]
                    
                    context += f"\n{content}\n"
                    
                    if post_id and post_id in other_chunks:
                        context += other_chunks[post_id]["metadata"]["content"][:400]
            
            chunk = f"# {title}\n\n{context if context else content}"
            chunks.append(chunk)
            
        return chunks

    def delete_index(self, confirm: bool = True) -> bool:
        """Delete the Pinecone index."""
        if not self.index:
            print("No active index to delete")
            return False
            
        try:
            # Get index name from the index object directly
            index_name = self.index._index_name

            if confirm:
                answer = input(f"Type 'y' to confirm deletion of index '{index_name}'...\n>> ")
                if answer.lower() != 'y':
                    print("Deletion Cancelled")
                    return False
                    
            self.pc.delete_index(index_name)
            self.index = None
            print(f"Index '{index_name}' Deleted!")
            return True
            
        except Exception as e:
            print(f"Error deleting index: {str(e)}")
            return False

def main():
    # Initialize with API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    
    if not openai_api_key or not pinecone_api_key:
        print("Error: Missing API keys. Please check your .env file.")
        return
    
    try:
        # Create processor instance
        processor = PDFProcessor(openai_api_key, pinecone_api_key)
        
        # Create index
        stats = processor.create_index("pdf-embeddings")
        print("Index Stats:", stats)
        
        # Process and index a PDF with validation
        doc_info = processor.read_pdf("textbook.pdf")
        if doc_info:
            # Ask user about overwrite preference
            overwrite = input("Overwrite if document already exists? (y/n): ").lower() == 'y'
            
            num_chunks, was_overwritten = processor.index_document(doc_info, overwrite=overwrite)
            if num_chunks > 0:
                print(f"{'Overwrote and indexed' if was_overwritten else 'Indexed'} {num_chunks} chunks")
            else:
                print("No new chunks were indexed")
            
            # Try a query
            query_text = "Why did we not anticipate discovery of such a rich, diverse first-person record of womens military service."
            print(f"\nQuerying: {query_text}")
            results = processor.query(query_text)
            
            if results:
                print("\nQuery Results:")
                for i, result in enumerate(results, 1):
                    print(f"\nResult {i}:")
                    print("-" * 80)
                    print(result[:400] + "..." if len(result) > 400 else result)
                    print("-" * 80)
            else:
                print("No matching results found")
            
            # Cleanup
            if input("\nType 'y' to delete the index, any other key to keep it...\n>> ").lower() == 'y':
                processor.delete_index(confirm=False)  # Already confirmed above
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()