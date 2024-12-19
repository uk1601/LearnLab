# scripts/s3_helper.py

import os
import boto3
from botocore.exceptions import ClientError
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client('s3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket = os.getenv('S3_BUCKET_NAME')
        self.prefix = os.getenv('S3_PREFIX', 'raw_pdfs/')
        self.download_dir = os.getenv('PDF_INPUT_DIRECTORY', '/opt/airflow/data')

    def list_pdfs(self) -> List[dict]:
        """List all PDFs in the S3 bucket/prefix."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.prefix
            )
            
            pdfs = []
            for obj in response.get('Contents', []):
                if obj['Key'].lower().endswith('.pdf'):
                    pdfs.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return pdfs
        except ClientError as e:
            logger.error(f"Error listing S3 objects: {str(e)}")
            raise

    def download_pdf(self, s3_key: str) -> Optional[str]:
        """Download a PDF from S3 to data directory."""
        try:
            # Ensure directory exists
            os.makedirs(self.download_dir, exist_ok=True)
            
            # Create local file path
            local_path = os.path.join(self.download_dir, os.path.basename(s3_key))
            
            # Download file
            self.s3_client.download_file(
                Bucket=self.bucket,
                Key=s3_key,
                Filename=local_path
            )
            logger.info(f"Downloaded {s3_key} to {local_path}")
            
            return local_path
        except ClientError as e:
            logger.error(f"Error downloading {s3_key}: {str(e)}")
            return None

    def download_pdfs(self) -> List[str]:
        """Download all PDFs to the data directory."""
        local_paths = []
        pdfs = self.list_pdfs()
        
        for pdf in pdfs:
            local_path = self.download_pdf(pdf['key'])
            if local_path:
                local_paths.append(local_path)
                
        logger.info(f"Downloaded {len(local_paths)} PDFs to {self.download_dir}")
        return local_paths

    def clear_data_directory(self):
        """Clear all PDFs from the data directory."""
        try:
            for file in os.listdir(self.download_dir):
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(self.download_dir, file)
                    os.remove(file_path)
                    logger.info(f"Removed {file_path}")
        except Exception as e:
            logger.error(f"Error clearing data directory: {str(e)}")