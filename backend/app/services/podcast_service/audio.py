from typing import Protocol, Tuple, Optional
from fastapi import UploadFile, HTTPException
from uuid import UUID
import aiofiles
import subprocess
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from app.core.logger import setup_logger, log_error
import os
import logging
from datetime import timedelta

from app.core.config import settings
from .s3 import S3Service


class IAudioService(Protocol):
    async def upload_podcast(
        self, 
        file: UploadFile, 
        user_id: UUID,
        validate_duration: bool = True
    ) -> Tuple[str, int]:
        pass
    
    async def get_streaming_url(
        self, 
        s3_key: str, 
        start_position: int = 0
    ) -> str:
        pass
    
    async def validate_audio_format(
        self, 
        file: UploadFile
    ) -> bool:
        pass
    
    async def get_audio_duration(
        self, 
        file: UploadFile
    ) -> int:
        pass
    
    async def process_chunk(
        self,
        file: UploadFile,
        chunk_start: int,
        chunk_size: int
    ) -> bytes:
        pass

logger = setup_logger(__name__)
class AudioService:
    def __init__(self, s3_service: S3Service):
        self.s3_service = s3_service
        self.ALLOWED_FORMATS = ["mp3", "wav", "m4a", "ogg"]
        self.MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
        logger.info("AudioService initialized with max file size: %sMB", self.MAX_FILE_SIZE / (1024 * 1024))

    async def _save_temp_file(self, file: UploadFile) -> str:
        """Helper method to save upload file to temporary location"""
        temp_file_path = f"/tmp/{file.filename}"
        logger.debug("Saving temporary file to: %s", temp_file_path)
        
        try:
            async with aiofiles.open(temp_file_path, 'wb') as out_file:
                # Read in chunks to handle large files
                chunk_size = 1024 * 1024  # 1MB chunks
                total_size = 0
                
                while chunk := await file.read(chunk_size):
                    total_size += len(chunk)
                    if total_size > self.MAX_FILE_SIZE:
                        raise HTTPException(
                            status_code=400,
                            detail=f"File size exceeds maximum limit of {self.MAX_FILE_SIZE/1024/1024}MB"
                        )
                    await out_file.write(chunk)
                
                logger.debug("Successfully wrote temporary file. Total size: %s bytes", total_size)
                
            # Reset file position for future reads
            await file.seek(0)
            return temp_file_path
            
        except HTTPException:
            raise
        except Exception as e:
            log_error(logger, e, {
                'filename': file.filename,
                'operation': 'save_temp_file'
            })
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise HTTPException(
                status_code=500,
                detail="Failed to process uploaded file"
            )

    async def get_audio_duration_from_s3(self, s3_key: str) -> int:
        """Get duration of audio file already in S3"""
        # Download to temporary file
        temp_file = await self.s3_service.download_to_temp(s3_key)
        try:
            # Get duration using existing method
            return await self.get_audio_duration(temp_file)
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    async def upload_podcast(
        self, 
        file: UploadFile, 
        user_id: UUID,
        validate_duration: bool = True
    ) -> Tuple[str, int]:
        """Upload a podcast file to S3 and return its key and duration"""
        logger.info("Starting podcast upload process for user %s, file: %s", user_id, file.filename)
        
        if not await self.validate_audio_format(file):
            logger.warning("Invalid audio format attempted: %s", file.filename)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audio format. Supported formats: {', '.join(self.ALLOWED_FORMATS)}"
            )

        temp_file_path = None
        try:
            temp_file_path = await self._save_temp_file(file)
            
            duration = 0
            if validate_duration:
                duration = await self.get_audio_duration(temp_file_path)
                logger.info("Audio duration validated: %s seconds", duration)

            s3_key = f"podcasts/{user_id}/{file.filename}"
            logger.debug("Uploading to S3 with key: %s", s3_key)
            
            await self.s3_service.upload_file(temp_file_path, s3_key)
            logger.info("Successfully uploaded podcast to S3: %s", s3_key)
            
            return s3_key, duration

        except Exception as e:
            log_error(logger, e, {
                'user_id': str(user_id),
                'filename': file.filename,
                'operation': 'upload_podcast'
            })
            raise
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug("Cleaned up temporary file: %s", temp_file_path)

    async def validate_audio_format(self, file: UploadFile) -> bool:
        """Validate if the uploaded file is in an acceptable audio format"""
        logger.debug("Validating audio format for file: %s", file.filename)
        
        if not file.filename:
            logger.warning("File upload attempted with no filename")
            return False
            
        file_ext = file.filename.split('.')[-1].lower()
        is_valid = file_ext in self.ALLOWED_FORMATS
        
        if not is_valid:
            logger.warning("Invalid file format attempted: %s", file_ext)
        
        return is_valid

    async def get_audio_duration(self, file_path: str) -> int:
        """Get the duration of an audio file in seconds"""
        logger.debug("Getting audio duration for file: %s", file_path)
        
        try:
            audio = AudioSegment.from_file(file_path)
            duration = len(audio) / 1000  # Convert milliseconds to seconds
            
            if duration <= 0:
                raise ValueError("Invalid audio duration")
            
            logger.debug("Successfully got audio duration: %s seconds", duration)
            return int(duration)
                
        except CouldntDecodeError as e:
            logger.warning("Failed to decode audio file: %s", file_path)
            raise HTTPException(
                status_code=400,
                detail="Invalid audio format. Please upload a valid audio file."
            )
        except Exception as e:
            log_error(logger, e, {
                'file_path': file_path,
                'operation': 'get_audio_duration'
            })
            raise HTTPException(
                status_code=400,
                detail="Unable to process audio file. Please ensure it's a valid audio file."
            )

    async def get_streaming_url(
        self,
        s3_key: str,
        start_position: int = 0
    ) -> str:
        """Get a presigned URL for streaming with range support"""
        logger.debug("Generating streaming URL for: %s, start position: %s", s3_key, start_position)
        
        try:
            url = await self.s3_service.get_presigned_url(
                s3_key,
                expiry_seconds=3600,  # 1 hour
                query_params={"start": start_position} if start_position > 0 else None
            )
            return url
        except Exception as e:
            log_error(logger, e, {
                's3_key': s3_key,
                'start_position': start_position,
                'operation': 'get_streaming_url'
            })
            raise

    async def process_chunk(
        self, 
        file: UploadFile, 
        chunk_start: int, 
        chunk_size: int
    ) -> bytes:
        """Process an audio chunk for streaming"""
        logger.debug("Processing audio chunk: start=%s, size=%s", chunk_start, chunk_size)
        
        temp_file_path = None
        try:
            temp_file_path = await self._save_temp_file(file)
            audio = AudioSegment.from_file(temp_file_path)
            chunk = audio[chunk_start:chunk_start + chunk_size]
            return chunk.raw_data

        except Exception as e:
            log_error(logger, e, {
                'filename': file.filename,
                'chunk_start': chunk_start,
                'chunk_size': chunk_size,
                'operation': 'process_chunk'
            })
            raise HTTPException(
                status_code=500,
                detail="Failed to process audio chunk"
            )
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
