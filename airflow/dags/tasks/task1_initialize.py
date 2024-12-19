# airflow/dags/tasks/task1_initialize.py

import os
import logging
from pathlib import Path
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

def initialize_resources(**context) -> bool:
    """
    Initialize OpenAI encoder and Pinecone resources.
    Instead of passing the PDFProcessor object via XCom, 
    we'll initialize it in each task that needs it.
    """
    try:
        # Get API keys from environment
        openai_api_key = os.getenv('OPENAI_API_KEY')
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        index_name = os.getenv('PINECONE_INDEX_NAME', 'pdf-semantic-chunking')
        
        if not openai_api_key or not pinecone_api_key:
            raise ValueError("Missing required API keys in environment variables")
        
        logger.info("Initializing PDFProcessor...")
        processor = PDFProcessor(
            openai_api_key=openai_api_key,
            pinecone_api_key=pinecone_api_key,
            index_name=index_name
        )
        
        # Create/initialize index
        index_name = os.getenv('PINECONE_INDEX_NAME', 'pdf-semantic-chunking')
        logger.info(f"Creating/connecting to Pinecone index: {index_name}")
        
        stats = processor.create_index(index_name=index_name)
        logger.info(f"Index initialized with stats: {stats}")

        # Instead of passing the processor object, we'll pass the initialization status
        context['task_instance'].xcom_push(
            key='index_info', 
            value={
                'index_name': index_name,
                'dimension': stats.get('dimension'),
                'total_vectors': stats.get('total_vector_count'),
                'initialization_success': True
            }
        )
        
        logger.info("Successfully initialized resources")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing resources: {str(e)}")
        # Push error information to XCom
        context['task_instance'].xcom_push(
            key='index_info',
            value={
                'initialization_success': False,
                'error': str(e)
            }
        )
        raise

if __name__ == "__main__":
    # For local testing
    try:
        class MockTaskInstance:
            def xcom_push(self, key, value):
                print(f"Would push to XCom - key: {key}, value: {value}")
                
        initialize_resources(context={'task_instance': MockTaskInstance()})
        print("Local test successful")
    except Exception as e:
        print(f"Local test failed: {str(e)}")