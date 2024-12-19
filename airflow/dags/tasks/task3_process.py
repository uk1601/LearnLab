# airflow/dags/tasks/task3_process.py

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

def process_documents(**context) -> bool:
    """Process validated PDF documents."""
    try:
        # Check if previous task was successful
        pdf_files_info = context['task_instance'].xcom_pull(
            task_ids='scan_and_validate_pdfs',
            key='pdf_files_info'
        )
        
        if not pdf_files_info or pdf_files_info.get('status') != 'success':
            raise ValueError("PDF scanning task failed or no valid PDFs found")

        # Initialize processor
        processor = initialize_processor()
        
        valid_pdfs = pdf_files_info.get('files', [])
        if not valid_pdfs:
            logger.warning("No valid PDFs to process")
            context['task_instance'].xcom_push(
                key='processed_docs_info',
                value={
                    'documents': [],
                    'count': 0,
                    'status': 'success'
                }
            )
            return True

        # Process each document
        processed_docs = []
        for pdf_info in valid_pdfs:
            try:
                # Read and process the PDF
                doc_info = processor.read_pdf(pdf_info['path'])
                
                if doc_info:
                    processed_docs.append({
                        'file_path': pdf_info['path'],
                        'hash': pdf_info['hash'],
                        'title': doc_info['title'],
                        'pages': doc_info['pages'],
                        'doc_id': doc_info['doc_id'],
                        'content': doc_info['content'],
                        'processed_date': doc_info['processed_date'],
                        'references': doc_info['references'],
                        'status': 'processed'
                    })
                    logger.info(f"Processed document: {doc_info['title']}")
                else:
                    logger.error(f"Failed to process document: {pdf_info['path']}")
                    
            except Exception as e:
                error_msg = f"Error processing {pdf_info['path']}: {str(e)}"
                logger.error(error_msg)
                processed_docs.append({
                    'file_path': pdf_info['path'],
                    'hash': pdf_info['hash'],
                    'status': 'failed',
                    'error': error_msg
                })

        # Store results in XCom
        successful = sum(1 for doc in processed_docs if doc['status'] == 'processed')
        context['task_instance'].xcom_push(
            key='processed_docs_info',
            value={
                'documents': processed_docs,
                'count': successful,
                'total': len(processed_docs),
                'status': 'success'
            }
        )
        
        logger.info(f"Processing complete: {successful}/{len(processed_docs)} documents successful")
        
        # Fail if no documents were processed successfully
        if successful == 0 and len(processed_docs) > 0:
            raise ValueError("Failed to process any documents successfully")
            
        return True
        
    except Exception as e:
        error_msg = f"Error in document processing: {str(e)}"
        logger.error(error_msg)
        context['task_instance'].xcom_push(
            key='processed_docs_info',
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
                    'files': [{
                        'path': 'test.pdf',
                        'hash': '123',
                        'title': 'Test PDF'
                    }]
                }
            
            def xcom_push(self, key, value):
                print(f"Would push to XCom - key: {key}, value: {value}")
        
        mock_context = {'task_instance': MockTaskInstance()}
        process_documents(**mock_context)
        print("Local test successful")
    except Exception as e:
        print(f"Local test failed: {str(e)}")