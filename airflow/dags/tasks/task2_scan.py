# airflow/dags/tasks/task2_scan.py

import os
import logging
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from scripts.pdf_processor import PDFProcessor
from scripts.s3_helper import S3Handler

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

def scan_and_validate_pdfs(**context) -> bool:
    """Scan directory for PDFs and validate them."""
    try:
        # Check if initialization was successful
        init_status = context['task_instance'].xcom_pull(
            task_ids='initialize_resources', 
            key='index_info'
        )
        
        if not init_status or not init_status.get('initialization_success'):
            raise ValueError("Resource initialization failed")

        # Initialize processor
        processor = initialize_processor()

        # Initialize S3 helper
        s3_handler = S3Handler()

        # Download PDFs from S3 (new)
        pdf_paths = s3_handler.download_pdfs()
        logger.info(f"Downloaded {len(pdf_paths)} PDFs from S3")
        
        if not pdf_paths:
            logger.warning("No PDF files found in S3")
            context['task_instance'].xcom_push(key='pdf_files_info', value={
                'files': [],
                'count': 0,
                'status': 'success'
            })
            return True

        # Process each PDF
        valid_pdfs = []
        for pdf_path in pdf_paths:
            try:
                # Read PDF to validate and get metadata
                doc_info = processor.read_pdf(pdf_path)

                if doc_info:
                    # Calculate document hash
                    doc_hash = processor.calculate_document_hash(doc_info["content"], doc_info)
                    exists, _ = processor.check_document_exists(doc_hash)

                    if not exists or os.getenv('OVERWRITE_EXISTING', 'false').lower() == 'true':
                        valid_pdfs.append({
                            'path': pdf_path,
                            'hash': doc_hash,
                            'title': doc_info['title'],
                            'pages': doc_info['pages'],
                            'doc_id': doc_info['doc_id']
                        })
                        logger.info(f"Validated PDF: {os.path.basename(pdf_path)}")
                    else:
                        logger.info(f"Skipping existing document: {os.path.basename(pdf_path)}")
            except Exception as e:
                logger.error(f"Error processing {os.path.basename(pdf_path)}: {str(e)}")

        # Store results in XCom
        context['task_instance'].xcom_push(
            key='pdf_files_info',
            value={
                'files': valid_pdfs,
                'count': len(valid_pdfs),
                'total_files': len(pdf_paths),
                'status': 'success'
            }
        )

        logger.info(f"Validation complete: {len(valid_pdfs)}/{len(pdf_paths)} PDFs valid")
        return True
    
    except Exception as e:
        error_msg = f"Error in scan_and_validate_pdfs: {str(e)}"
        logger.error(error_msg)
        context['task_instance'].xcom_push(
            key='pdf_files_info',
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
                return {'initialization_success': True}
            
            def xcom_push(self, key, value):
                print(f"Would push to XCom - key: {key}, value: {value}")
        
        mock_context = {'task_instance': MockTaskInstance()}
        scan_and_validate_pdfs(**mock_context)
        print("Local test successful")
    except Exception as e:
        print(f"Local test failed: {str(e)}")