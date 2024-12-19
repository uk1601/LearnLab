# airflow/dags/pdf_processing_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Import tasks
from tasks.task1_initialize import initialize_resources
from tasks.task2_scan import scan_and_validate_pdfs
from tasks.task3_process import process_documents
from tasks.task4_embeddings import create_embeddings
from tasks.task5_upload import upload_to_pinecone

# Default arguments for tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
with DAG(
    'pdf_processing_pipeline',
    default_args=default_args,
    description='Process PDFs, create embeddings, and upload to Pinecone',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,  # Only one run at a time
    tags=['pdf', 'pinecone', 'embeddings'],
) as dag:
    
    # Task 1: Initialize Resources
    init_resources = PythonOperator(
        task_id='initialize_resources',
        python_callable=initialize_resources,
        retries=2,  # More retries for initialization
        retry_delay=timedelta(minutes=2),
    )
    
    # Task 2: Scan and Validate PDFs
    scan_pdfs = PythonOperator(
        task_id='scan_and_validate_pdfs',
        python_callable=scan_and_validate_pdfs,
        retries=2,
    )
    
    # Task 3: Process Documents
    process_docs = PythonOperator(
        task_id='process_documents',
        python_callable=process_documents,
    )
    
    # Task 4: Create Embeddings
    create_embeds = PythonOperator(
        task_id='create_embeddings',
        python_callable=create_embeddings,
        retries=2,  # More retries for API calls
        retry_delay=timedelta(minutes=2),
    )
    
    # Task 5: Upload to Pinecone
    upload_vectors = PythonOperator(
        task_id='upload_to_pinecone',
        python_callable=upload_to_pinecone,
        retries=3,  # More retries for uploads
        retry_delay=timedelta(minutes=2),
    )
    
    # Set dependencies
    init_resources >> scan_pdfs >> process_docs >> create_embeds >> upload_vectors

    # Add doc strings
    dag.doc_md = """
    # PDF Processing Pipeline
    
    This DAG implements a pipeline for processing PDFs and creating semantic search capabilities:
    
    1. Initialize resources and connections
    2. Scan and validate PDF files
    3. Process and extract content from PDFs
    4. Create embeddings for the content
    5. Upload vectors to Pinecone index
    
    ## Dependencies
    - OpenAI API access
    - Pinecone account and API key
    - PDF files in the configured input directory
    
    ## Configuration
    Set the following environment variables:
    - OPENAI_API_KEY
    - PINECONE_API_KEY
    - PINECONE_INDEX_NAME
    - PDF_INPUT_DIRECTORY
    """