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
    def __init__(self, openai_api_key: str, pinecone_api_key: str, pinecone_index_name: str):
        """Initialize the PDF processor with necessary components."""
        print(f"----------------------PDF Processor Initialisation----------------------\n")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv("PINECONE_INDEX_NAME","pdf-semantic-chunking")
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
            # plot_splits=True,
            enable_statistics=True
        )
        
        self.index = None
        self.create_index(index_name=pinecone_index_name)

    def create_index(self, index_name: str = "pdf-semantic-chunking1"):
        """Create and initialize Pinecone index."""
        print(f"----------------------Index Creation----------------------\n")
        # Setup serverless specification
        spec = ServerlessSpec(cloud="aws", region="us-east-1")
        
        # Check if index exists
        if index_name in self.pc.list_indexes().names():
            # If exists, just connect to it
            self.index = self.pc.Index(index_name)
            logger.info(f"Connected to existing index: {index_name}")
        else:
            # Create new index if it doesn't exist
            self.pc.create_index(
                name=index_name,
                dimension=self.dims,
                metric='dotproduct',
                spec=spec
            )
            # Wait for index to be initialized
            while not self.pc.describe_index(index_name).status['ready']:
                time.sleep(5)
            
            # Connect to index
            self.index = self.pc.Index(index_name)

            logger.info(f"Created and initialized new index: {index_name}")
        
        time.sleep(5)  # Small delay to ensure connection is established
        print(f"Pinecone index connected with {self.dims} dimensions")
        return self.index.describe_index_stats()
        # """Create and initialize Pinecone index."""
        # # Setup serverless specification
        # spec = ServerlessSpec(cloud="aws", region="us-east-1")
        
        # # Create index if it doesn't exist
        # if index_name not in self.pc.list_indexes().names():
        #     self.pc.create_index(
        #         name=index_name,
        #         dimension=self.dims,
        #         metric='dotproduct',
        #         spec=spec
        #     )
        #     # Wait for index to be initialized
        #     while not self.pc.describe_index(index_name).status['ready']:
        #         time.sleep(1)
        
        # # Connect to index
        # self.index = self.pc.Index(index_name)
        # time.sleep(1)
        # return self.index.describe_index_stats()

    def build_chunk(self, title: str, content: str) -> str:
        """Format chunk with title for embedding."""
        return f"# {title}\n{content}"

    def calculate_document_hash(self, content: str, metadata: Dict[str, Any]) -> str:
        """Calculate a unique hash for a document based on its content and metadata."""
        hash_input = f"{content}{metadata.get('title', '')}{metadata.get('processed_date', '')}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def check_document_exists(self, doc_hash: str) -> Tuple[bool, List[str]]:
        """Check if a document with the same hash exists in the index."""
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
        """Delete specific chunks from the index."""
        try:
            if chunk_ids:
                self.index.delete(ids=chunk_ids)
            return True
        except Exception as e:
            print(f"Error deleting chunks: {str(e)}")
            return False

    def build_metadata(self, doc: Dict[str, Any], doc_splits: List[DocumentSplit]) -> List[Dict[str, Any]]:
        """Create metadata for each chunk including contextual information."""
        print(f"----------------------Metadata Building----------------------\n")
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

    def read_pdf(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Read PDF and extract content with metadata."""
        print(f"----------------------PDF Processing:PARSING----------------------\n")
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

    def index_document(self, doc_info: Dict[str, Any], batch_size: int = 128, overwrite: bool = False) -> Tuple[int, bool]:
        """Index document chunks with validation."""
        print(f"----------------------Document Indexing----------------------\n")
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
            
        # Calculate document hash
        doc_hash = self.calculate_document_hash(doc_info["content"], doc_info)
        
        # Check if document exists
        exists, existing_chunks = self.check_document_exists(doc_hash)
        
        if exists and not overwrite:
            print(f"Document '{doc_info['title']}' already exists in the index.")
            return 0, False
            
        if exists and overwrite:
            if not self.delete_document_chunks(existing_chunks):
                raise Exception("Failed to delete existing document chunks")
        
        # Create splits
        splits = self.splitter([doc_info["content"]])
        
        # Create metadata
        metadata = self.build_metadata(doc=doc_info, doc_splits=splits)
        
        # Add document hash
        for m in metadata:
            m["doc_hash"] = doc_hash
        
        # Process in batches
        for i in range(0, len(splits), batch_size):
            i_end = min(len(splits), i+batch_size)
            metadata_batch = metadata[i:i_end]
            
            ids = [m["id"] for m in metadata_batch]
            content = [self.build_chunk(title=x["title"], content=x["content"]) 
                      for x in metadata_batch]
            
            embeds = self.encoder(content)
            self.index.upsert(vectors=zip(ids, embeds, metadata_batch))
            
        return len(splits), exists

    def get_available_pdfs(self) -> List[str]:
        """Retrieve list of all indexed PDF titles."""
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
        
        # Query with dummy vector to get unique titles
        response = self.index.query(
            vector=[0] * self.dims,
            top_k=10000,  # Large number to get all possible matches
            include_metadata=True
        )
        
        # Extract unique titles from metadata
        titles = set()
        for match in response.matches:
            if 'title' in match.metadata:
                titles.add(match.metadata['title'])
        
        return sorted(list(titles))

    def query(self, text: str, pdf_title: Optional[str] = None, top_k: int = 3) -> List[str]:
        """Query the index for similar chunks, optionally filtering by PDF title."""
        print(f"----------------------QUERY----------------------\nDEBUG in QUERY: {self.index.describe_index_stats()}")
        print(f"DEBUG in QUERY: {pdf_title}")
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
            
        if not pdf_title:
            raise ValueError("PDF title is required for querying.")
    
        # Create query embedding
        xq = self.encoder([text])[0]
        # Prepare filter if pdf_title is specified
        filter_dict = {"title": pdf_title}
        
        # Query index
        matches = self.index.query(
            vector=xq,
            top_k=top_k,
            filter=filter_dict,
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

        print(f"Query Results for '{pdf_title}'")
        print(f"Number of Matches: {len(chunks)}")
        print(f"\n----------------------\n")
            
        return chunks

    def delete_index(self, confirm: bool = True) -> bool:
        """Delete the Pinecone index."""
        if not self.index:
            print("No active index to delete")
            return False
            
        try:
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
        
    async def delete_document_by_file_id(self, file_id: str) -> bool:
        """Delete all vectors associated with a file ID using ID-based deletion."""
        try:
            if not self.index:
                raise ValueError("Index not initialized.")

            # First, query to get all vector IDs associated with this file
            # We'll use a dummy vector for the query
            response = self.index.query(
                vector=[0] * self.dims,
                top_k=10000,  # Large enough to get all chunks
                include_metadata=True
            )

            # Filter matches to find those associated with our file_id
            chunk_ids = []
            for match in response.matches:
                if match.metadata.get("file_id") == file_id:
                    chunk_ids.append(match.id)

            if chunk_ids:
                # Delete vectors by their IDs
                self.index.delete(ids=chunk_ids)
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting vectors for file {file_id}: {str(e)}")
            return False