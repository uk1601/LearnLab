# airflow/dags/tasks/task5_upload.py

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from scripts.pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path('/opt/airflow/.env')
load_dotenv(dotenv_path=env_path)

def initialize_processor() -> PDFProcessor:
    """Initialize the PDFProcessor with environment variables."""
    return PDFProcessor(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        pinecone_api_key=os.getenv('PINECONE_API_KEY'),
        index_name=os.getenv('PINECONE_INDEX_NAME', 'pdf-semantic-chunking')
    )

def upload_document_batches(processor: PDFProcessor, doc_data: Dict, batch_size: int) -> Tuple[int, List[str]]:
    """Upload document chunks in batches."""
    uploaded_chunks = 0
    errors = []
    
    try:
        splits = doc_data['splits']
        metadata = doc_data['metadata']
        
        # Process in batches
        for i in range(0, len(splits), batch_size):
            try:
                i_end = min(len(splits), i + batch_size)
                metadata_batch = metadata[i:i_end]
                
                # Prepare vectors for upload
                ids = [m['id'] for m in metadata_batch]
                contents = [processor.build_chunk(title=m['title'], content=m['content']) 
                           for m in metadata_batch]
                
                # Create embeddings and upload
                embeds = processor.encoder(contents)
                processor.index.upsert(vectors=zip(ids, embeds, metadata_batch))
                
                uploaded_chunks += len(metadata_batch)
                logger.info(f"Uploaded batch of {len(metadata_batch)} chunks")
                
            except Exception as e:
                error_msg = f"Error uploading batch {i//batch_size}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                
        return uploaded_chunks, errors
        
    except Exception as e:
        error_msg = f"Error in batch upload process: {str(e)}"
        logger.error(error_msg)
        return uploaded_chunks, [error_msg]

def upload_to_pinecone(**context) -> bool:
    """Upload documents with embeddings to Pinecone."""
    try:
        # Check if previous task was successful
        embeddings_info = context['task_instance'].xcom_pull(
            task_ids='create_embeddings',
            key='embeddings_info'
        )
        
        if not embeddings_info or embeddings_info.get('status') != 'success':
            raise ValueError("Embedding creation task failed")

        # Initialize processor
        processor = initialize_processor()
        
        # Get batch size from environment
        batch_size = int(os.getenv('UPLOAD_BATCH_SIZE', '100'))
        documents = embeddings_info.get('documents', [])
        successful_docs = [doc for doc in documents if doc['status'] == 'success']
        
        if not successful_docs:
            logger.warning("No documents with embeddings to upload")
            context['task_instance'].xcom_push(
                key='upload_info',
                value={
                    'uploaded_chunks': 0,
                    'status': 'success'
                }
            )
            return True

        logger.info(f"Starting upload for {len(successful_docs)} documents")
        
        # Upload statistics
        total_uploaded = 0
        total_errors = []
        upload_results = []
        
        # Process each document
        for doc in successful_docs:
            logger.info(f"Uploading chunks for document: {doc['title']}")
            uploaded_chunks, errors = upload_document_batches(
                processor=processor,
                doc_data=doc,
                batch_size=batch_size
            )
            
            total_uploaded += uploaded_chunks
            total_errors.extend(errors)
            
            upload_results.append({
                'title': doc['title'],
                'doc_id': doc['doc_id'],
                'chunks_uploaded': uploaded_chunks,
                'expected_chunks': doc['num_chunks'],
                'status': 'success' if not errors else 'partial',
                'errors': errors
            })

        # Store results in XCom
        context['task_instance'].xcom_push(
            key='upload_info',
            value={
                'uploaded_chunks': total_uploaded,
                'total_errors': len(total_errors),
                'upload_results': upload_results,
                'documents_processed': len(successful_docs),
                'status': 'success'
            }
        )
        
        logger.info(
            f"Upload complete: {total_uploaded} chunks uploaded from "
            f"{len(successful_docs)} documents with {len(total_errors)} errors"
        )
        
        # Fail if nothing was uploaded
        if total_uploaded == 0:
            raise ValueError("Failed to upload any chunks to Pinecone")
            
        return True
        
    except Exception as e:
        error_msg = f"Error in Pinecone upload: {str(e)}"
        logger.error(error_msg)
        context['task_instance'].xcom_push(
            key='upload_info',
            value={
                'status': 'error',
                'error': error_msg
            }
        )
        raise

if __name__ == "__main__":
    # For local testing
    try:
        class MockTaskInstance:
            def xcom_pull(self, task_ids, key):
                return {
                    'status': 'success',
                    'documents': [{
                        'title': 'Test Doc',
                        'doc_id': '123',
                        'splits': ['content1', 'content2'],
                        'metadata': [
                            {'id': '1', 'title': 'Test', 'content': 'content1'},
                            {'id': '2', 'title': 'Test', 'content': 'content2'}
                        ],
                        'num_chunks': 2,
                        'status': 'success'
                    }]
                }
            
            def xcom_push(self, key, value):
                print(f"Would push to XCom - key: {key}, value: {value}")
        
        mock_context = {'task_instance': MockTaskInstance()}
        upload_to_pinecone(**mock_context)
        print("Local test successful")
    except Exception as e:
        print(f"Local test failed: {str(e)}")