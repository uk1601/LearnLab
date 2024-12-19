from typing import Protocol, Optional, Dict
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import logging
from fastapi import HTTPException
import time
from uuid import UUID

from app.core.config import settings
from app.core.logger import setup_logger, log_error

logger = setup_logger(__name__)


class S3Service:
    def __init__(self):
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.AWS_BUCKET_NAME
            logger.info(f"Initialized S3 service with bucket: {self.bucket_name}")
        except Exception as e:
            log_error(logger, e, {'message': 'Failed to initialize S3 service'})
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize S3 service"
            )

    async def upload_file(
        self,
        file_path: str,
        s3_key: str
    ) -> bool:
        """Upload a file to S3"""
        start_time = time.time()
        logger.info(f"Starting file upload. Path: {file_path}, Key: {s3_key}")
        
        try:
            extra_args = {}
            
            # Set content type based on file extension
            if s3_key.endswith('.txt'):
                extra_args['ContentType'] = 'text/plain'
            elif s3_key.endswith('.vtt'):
                extra_args['ContentType'] = 'text/vtt'
            elif s3_key.endswith(('.mp3', '.m4a', '.wav', '.ogg')):
                extra_args['ContentType'] = 'audio/mpeg'

            # Set additional headers
            extra_args.update({
                'CacheControl': 'max-age=31536000',  # 1 year
                'ACL': 'private'
            })

            # Upload file
            with open(file_path, 'rb') as file_obj:
                self.s3_client.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs=extra_args
                )

            elapsed_time = time.time() - start_time
            logger.info(f"File upload successful. Time taken: {elapsed_time:.2f}s")
            return True

        except ClientError as e:
            log_error(logger, e, {
                'file_path': file_path,
                's3_key': s3_key,
                'operation': 'upload',
                'error_code': e.response['Error']['Code']
            })
            raise HTTPException(
                status_code=500,
                detail=f"AWS S3 error: {e.response['Error']['Message']}"
            )
        except Exception as e:
            log_error(logger, e, {
                'file_path': file_path,
                's3_key': s3_key,
                'operation': 'upload'
            })
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )

    async def get_presigned_url(
        self,
        s3_key: str,
        expiry_seconds: int = 3600,
        query_params: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate a presigned URL for accessing an S3 object"""
        logger.debug(f"Generating presigned URL for key: {s3_key}")
        
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': s3_key
            }

            # Add query parameters if provided
            if query_params:
                params['QueryParameters'] = query_params

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiry_seconds
            )
            logger.debug(f"Generated presigned URL with expiry: {expiry_seconds}s")
            return url

        except ClientError as e:
            log_error(logger, e, {
                's3_key': s3_key,
                'operation': 'generate_url',
                'error_code': e.response['Error']['Code']
            })
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate download URL: {e.response['Error']['Message']}"
            )
        except Exception as e:
            log_error(logger, e, {
                's3_key': s3_key,
                'operation': 'generate_url'
            })
            raise HTTPException(
                status_code=500,
                detail="Failed to generate access URL"
            )

    async def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3"""
        logger.info(f"Attempting to delete file with key: {s3_key}")
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Successfully deleted file: {s3_key}")
            return True

        except ClientError as e:
            log_error(logger, e, {
                's3_key': s3_key,
                'operation': 'delete',
                'error_code': e.response['Error']['Code']
            })
            raise HTTPException(
                status_code=500,
                detail=f"AWS S3 error: {e.response['Error']['Message']}"
            )
        except Exception as e:
            log_error(logger, e, {
                's3_key': s3_key,
                'operation': 'delete'
            })
            raise HTTPException(
                status_code=500,
                detail="Failed to delete file from storage"
            )

    async def check_file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3"""
        logger.debug(f"Checking existence of file: {s3_key}")
        
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            log_error(logger, e, {
                's3_key': s3_key,
                'operation': 'check_exists',
                'error_code': e.response['Error']['Code']
            })
            raise HTTPException(
                status_code=500,
                detail="Failed to check file existence"
            )

    async def download_to_temp(self, s3_key: str) -> str:
        """
        Downloads a file from S3 to a temporary location and returns the local file path.
        """
        import tempfile
        import os

        logger.debug(f"Downloading file from S3: {s3_key}")

        try:
            # Create a temporary file
            temp_fd, temp_path = tempfile.mkstemp()
            os.close(temp_fd)  # Close the file descriptor

            # Download the file
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                temp_path
            )

            logger.debug(f"Successfully downloaded file to: {temp_path}")
            return temp_path

        except ClientError as e:
            log_error(logger, e, {
                's3_key': s3_key,
                'operation': 'download_to_temp',
                'error_code': e.response['Error']['Code']
            })
            raise HTTPException(
                status_code=500,
                detail=f"AWS S3 error: {e.response['Error']['Message']}"
            )
        except Exception as e:
            log_error(logger, e, {
                's3_key': s3_key,
                'operation': 'download_to_temp'
            })
            raise HTTPException(
                status_code=500,
                detail="Failed to download file from S3"
            )