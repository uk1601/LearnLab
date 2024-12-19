# First create a new file called s3_storage.py

import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
import re

class S3Storage:
    def __init__(self, bucket_name: str):
        """Initialize S3 storage handler"""
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be S3 compatible"""
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9-_.]', '_', filename)
        # Convert to lowercase for consistency
        return sanitized.lower()

    def upload_file(self, file_path: str, podcast_title: str, pdf_title: str) -> str:
        """
        Upload a file to S3 with organized folder structure
        Returns the S3 URL of the uploaded file
        """
        try:
            # Sanitize the podcast and PDF titles
            safe_podcast_title = self.sanitize_filename(podcast_title)
            safe_pdf_title = self.sanitize_filename(pdf_title)
            
            # Create the S3 key with folder structure: podcast/{pdf_title}/{podcast_title}_{timestamp}.mp3
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"podcast/{safe_pdf_title}/{safe_podcast_title}_{timestamp}.mp3"
            
            # Upload the file
            extra_args = {}
            extra_args['ContentType'] = 'audio/mpeg'
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            
            # Generate the S3 URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            # Remove the local file after successful upload
            os.remove(file_path)
            
            return url
            
        except ClientError as e:
            print(f"Error uploading to S3: {str(e)}")
            raise

    def list_podcasts(self, pdf_title: str = None) -> list:
        """
        List all podcasts in the bucket, optionally filtered by PDF title
        """
        try:
            prefix = "podcast/"
            if pdf_title:
                safe_pdf_title = self.sanitize_filename(pdf_title)
                prefix = f"podcast/{safe_pdf_title}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            podcasts = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    podcasts.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return podcasts
            
        except ClientError as e:
            print(f"Error listing S3 objects: {str(e)}")
            raise