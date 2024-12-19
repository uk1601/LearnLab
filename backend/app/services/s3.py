import boto3
from fastapi import UploadFile, HTTPException
from ..core.config import settings
from ..core.logger import setup_logger, log_error
from typing import Optional
import uuid
import time
from botocore.exceptions import BotoCoreError, ClientError
import tempfile
import os


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

    async def upload_file(self, file: UploadFile, user_id: uuid.UUID) -> str:
        """
        Uploads a file to S3 and returns the S3 key.
        Files are stored in a user-specific directory.
        """
        start_time = time.time()
        logger.info(f"Starting file upload. User: {user_id}, File: {file.filename}")

        try:
            # Generate a unique filename to avoid collisions
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            s3_key = f"users/{user_id}/{uuid.uuid4()}.{file_extension}"

            logger.debug(f"Generated S3 key: {s3_key}")
            logger.debug(f"File details - Size: {file.size}, Type: {file.content_type}")

            # Upload the file
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file.content_type
                }
            )

            elapsed_time = time.time() - start_time
            logger.info(f"File upload successful. Time taken: {elapsed_time:.2f}s")
            return s3_key

        except ClientError as e:
            log_error(logger, e, {
                'user_id': str(user_id),
                'filename': file.filename,
                'operation': 'upload',
                'error_code': e.response['Error']['Code']
            })
            raise HTTPException(
                status_code=500,
                detail=f"AWS S3 error: {e.response['Error']['Message']}"
            )
        except Exception as e:
            log_error(logger, e, {
                'user_id': str(user_id),
                'filename': file.filename,
                'operation': 'upload'
            })
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to S3"
            )

    async def generate_presigned_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """
        Generates a presigned URL for downloading a file.
        URL expires after the specified time (default 1 hour).
        """
        logger.debug(f"Generating presigned URL for key: {s3_key}")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            logger.debug(f"Generated presigned URL with expiry: {expires_in}s")
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
                detail="Failed to generate download URL"
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

    async def delete_file(self, s3_key: str) -> bool:
        """
        Deletes a file from S3.
        Returns True if successful, raises HTTPException otherwise.
        """
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
                detail="Failed to delete file from S3"
            )