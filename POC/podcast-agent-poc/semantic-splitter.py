import os
from getpass import getpass
from semantic_router.encoders import OpenAIEncoder
from semantic_router.splitters import RollingWindowSplitter
from semantic_router.utils.logger import logger
from semantic_router.schema import DocumentSplit
import PyPDF2
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

class PDFProcessor:
    def __init__(self, api_key: str):
        """Initialize the PDF processor with necessary components."""
        os.environ["OPENAI_API_KEY"] = api_key
        self.encoder = OpenAIEncoder(name="text-embedding-3-small")
        logger.setLevel("WARNING")
        
        self.splitter = RollingWindowSplitter(
            encoder=self.encoder,
            dynamic_threshold=True,
            min_split_tokens=100,
            max_split_tokens=500,
            window_size=2,
            plot_splits=True,
            enable_statistics=True
        )

    def read_pdf(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Read PDF and extract content with metadata."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                # Extract basic document metadata
                doc_info = {
                    "file_path": file_path,
                    "title": os.path.splitext(os.path.basename(file_path))[0],
                    "pages": len(pdf_reader.pages),
                    "content": text,
                    "processed_date": datetime.now().isoformat(),
                    "doc_id": f"doc_{hash(file_path)}",
                    "references": []  # Could be populated with reference extraction logic
                }
                return doc_info
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return None

    def build_chunk(self, title: str, content: str) -> str:
        """Format chunk with title for embedding."""
        return f"# {title}\n{content}"

    def build_metadata(self, doc: Dict[str, Any], doc_splits: List[DocumentSplit]) -> List[Dict[str, Any]]:
        """Create metadata for each chunk including contextual information."""
        metadata = []
        for i, split in enumerate(doc_splits):
            # Create unique chunk identifiers
            chunk_id = f"{doc['doc_id']}#{i}"
            prechunk_id = "" if i == 0 else f"{doc['doc_id']}#{i-1}"
            postchunk_id = "" if i+1 == len(doc_splits) else f"{doc['doc_id']}#{i+1}"
            
            # Get surrounding chunks for context
            prechunk = "" if i == 0 else doc_splits[i-1].content
            postchunk = "" if i+1 == len(doc_splits) else doc_splits[i+1].content
            
            metadata.append({
                "id": chunk_id,
                "title": doc["title"],
                "content": split.content,
                "prechunk": prechunk,
                "postchunk": postchunk,
                "prechunk_id": prechunk_id,
                "postchunk_id": postchunk_id,
                "doc_id": doc["doc_id"],
                "page_count": doc["pages"],
                "processed_date": doc["processed_date"],
                "token_count": split.token_count,
                "similarity_score": split.triggered_score,
                "references": doc["references"]
            })
        return metadata

    def process_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Process PDF document and return splits with metadata."""
        try:
            # Read document
            doc = self.read_pdf(file_path)
            if not doc:
                return None
            
            # Create splits
            splits = self.splitter([doc["content"]])
            
            # Create metadata
            metadata = self.build_metadata(doc, splits)
            
            # Create embedding-ready chunks
            embedding_chunks = [
                self.build_chunk(meta["title"], meta["content"]) 
                for meta in metadata
            ]
            
            # Return complete document processing results
            return {
                "doc_info": doc,
                "splits": splits,
                "metadata": metadata,
                "embedding_chunks": embedding_chunks,
                "statistics": {
                    "total_chunks": len(splits),
                    "average_chunk_size": sum(s.token_count for s in splits) / len(splits),
                    "processing_date": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return None

def main():
    # Example usage
    api_key = os.getenv("OPENAI_API_KEY")
    processor = PDFProcessor(api_key)
    
    # Process document
    result = processor.process_document("textbook.pdf")
    
    if result:
        # Print processing statistics
        print("\nDocument Processing Statistics:")
        print(f"Total chunks created: {result['statistics']['total_chunks']}")
        print(f"Average chunk size: {result['statistics']['average_chunk_size']:.2f} tokens")
        
        # Print first few chunks with metadata
        print("\nSample Chunks with Metadata:")
        for i, (meta, chunk) in enumerate(zip(result['metadata'][:3], result['embedding_chunks'][:3])):
            print(f"\nChunk {i+1}:")
            print(f"ID: {meta['id']}")
            print(f"Token Count: {meta['token_count']}")
            print(f"Similarity Score: {meta['similarity_score']:.4f}")
            print("Content Preview:")
            print(chunk[:200] + "...")
            print("-" * 80)

if __name__ == "__main__":
    main()