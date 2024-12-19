# airflow/dags/tasks/task4_embeddings.py

import os
import logging
from pathlib import Path
from typing import Dict, List
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

def create_embeddings(**context) -> bool:
    """Create embeddings for processed documents."""
    try:
        # Check if previous task was successful
        processed_docs_info = context['task_instance'].xcom_pull(
            task_ids='process_documents',
            key='processed_docs_info'
        )
        
        if not processed_docs_info or processed_docs_info.get('status') != 'success':
            raise ValueError("Document processing task failed")

        # Initialize processor
        processor = initialize_processor()
        
        processed_docs = processed_docs_info.get('documents', [])
        successful_docs = [doc for doc in processed_docs if doc['status'] == 'processed']
        
        if not successful_docs:
            logger.warning("No processed documents to create embeddings for")
            context['task_instance'].xcom_push(
                key='embeddings_info',
                value={
                    'documents': [],
                    'total_chunks': 0,
                    'status': 'success'
                }
            )
            return True

        logger.info(f"Creating embeddings for {len(successful_docs)} documents")
        
        # Process each document
        documents_with_embeddings = []
        total_chunks = 0
        
        for doc in successful_docs:
            try:
                # Create splits
                logger.info(f"Creating splits for document: {doc['title']}")
                splits = processor.splitter([doc['content']])
                num_splits = len(splits)
                logger.info(f"Created {num_splits} splits")
                
                # Create metadata for chunks
                metadata = processor.build_metadata({
                    'title': doc['title'],
                    'doc_id': doc['doc_id'],
                    'pages': doc['pages'],
                    'content': doc['content'],
                    'references': doc['references'],
                    'processed_date': doc['processed_date']
                }, splits)
                
                # Add document hash to all chunks
                for m in metadata:
                    m['doc_hash'] = doc['hash']
                
                documents_with_embeddings.append({
                    'title': doc['title'],
                    'doc_id': doc['doc_id'],
                    'splits': [split.content for split in splits],  # Store only the content
                    'metadata': metadata,
                    'num_chunks': num_splits,
                    'status': 'success'
                })
                
                total_chunks += num_splits
                logger.info(f"Successfully created embeddings for {doc['title']}")
                
            except Exception as e:
                error_msg = f"Error creating embeddings for {doc['title']}: {str(e)}"
                logger.error(error_msg)
                documents_with_embeddings.append({
                    'title': doc['title'],
                    'doc_id': doc['doc_id'],
                    'status': 'failed',
                    'error': error_msg
                })

        # Store results in XCom
        successful = sum(1 for doc in documents_with_embeddings if doc['status'] == 'success')
        context['task_instance'].xcom_push(
            key='embeddings_info',
            value={
                'documents': documents_with_embeddings,
                'total_chunks': total_chunks,
                'successful_docs': successful,
                'total_docs': len(documents_with_embeddings),
                'status': 'success'
            }
        )
        
        logger.info(
            f"Embedding creation complete: {successful}/{len(documents_with_embeddings)} "
            f"documents successful, {total_chunks} total chunks"
        )
        
        # Fail if no documents were processed successfully
        if successful == 0 and len(documents_with_embeddings) > 0:
            raise ValueError("Failed to create embeddings for any documents")
            
        return True
        
    except Exception as e:
        error_msg = f"Error in embedding creation: {str(e)}"
        logger.error(error_msg)
        context['task_instance'].xcom_push(
            key='embeddings_info',
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
                        'content': 'Test content',
                        'doc_id': '123',
                        'status': 'processed',
                        'pages': 1
                    }]
                }
            
            def xcom_push(self, key, value):
                print(f"Would push to XCom - key: {key}, value: {value}")
        
        mock_context = {'task_instance': MockTaskInstance()}
        create_embeddings(**mock_context)
        print("Local test successful")
    except Exception as e:
        print(f"Local test failed: {str(e)}")