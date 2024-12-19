from typing import Protocol, Dict, Optional
from fastapi import UploadFile, HTTPException
from uuid import UUID
import aiofiles
import re
import os
import logging
from datetime import timedelta

from app.core.config import settings
from .s3 import S3Service

logger = logging.getLogger(__name__)
class ITranscriptService(Protocol):
    async def process_transcript(
        self,
        file: UploadFile,
        user_id: UUID,
        format: str = 'txt'
    ) -> Dict[str, str]:
        pass
    
    async def convert_to_vtt(
        self,
        text_content: str
    ) -> Optional[str]:
        pass
    
    async def get_transcript_url(
        self,
        s3_key: str
    ) -> str:
        pass
class TranscriptService:
    def __init__(self, s3_service: S3Service):
        self.s3_service = s3_service
        self.SUPPORTED_FORMATS = ['txt', 'vtt']
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for transcripts

    async def process_transcript(
        self,
        file: UploadFile,
        user_id: UUID,
        format: str = 'txt'
    ) -> Dict[str, str]:
        """Process and upload a transcript file"""
        
        if format not in self.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Create temporary file
        temp_file_path = f"/tmp/{file.filename}"
        try:
            async with aiofiles.open(temp_file_path, 'wb') as out_file:
                content = await file.read()
                if len(content) > self.MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File size exceeds maximum limit of {self.MAX_FILE_SIZE/1024/1024}MB"
                    )
                await out_file.write(content)

            # Read and validate content
            async with aiofiles.open(temp_file_path, 'r', encoding='utf-8') as in_file:
                content = await in_file.read()

            # Generate S3 keys
            txt_key = f"transcripts/{user_id}/{file.filename}"
            result = {"txt_key": txt_key}

            # Handle VTT conversion if needed
            if format == 'txt':
                vtt_content = await self.convert_to_vtt(content)
                if vtt_content:
                    vtt_key = f"transcripts/{user_id}/{os.path.splitext(file.filename)[0]}.vtt"
                    result["vtt_key"] = vtt_key
                    
                    # Save VTT file temporarily
                    vtt_temp_path = f"/tmp/{os.path.splitext(file.filename)[0]}.vtt"
                    async with aiofiles.open(vtt_temp_path, 'w', encoding='utf-8') as vtt_file:
                        await vtt_file.write(vtt_content)
                    
                    # Upload VTT file
                    await self.s3_service.upload_file(vtt_temp_path, vtt_key)
                    os.remove(vtt_temp_path)

            # Upload original transcript
            await self.s3_service.upload_file(temp_file_path, txt_key)
            
            return result

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    async def convert_to_vtt(self, text_content: str) -> Optional[str]:
        """Convert plain text transcript to WebVTT format"""
        
        try:
            lines = text_content.split('\n')
            vtt_content = ["WEBVTT", ""]
            current_time = 0
            words_per_segment = 10  # Adjust based on preference
            
            words = []
            for line in lines:
                words.extend(line.split())
            
            for i in range(0, len(words), words_per_segment):
                segment = words[i:i + words_per_segment]
                duration = len(' '.join(segment)) * 0.06  # Rough estimate of speaking time
                
                start_time = self._format_timestamp(current_time)
                current_time += duration
                end_time = self._format_timestamp(current_time)
                
                vtt_content.extend([
                    f"{start_time} --> {end_time}",
                    ' '.join(segment),
                    ""
                ])
            
            return '\n'.join(vtt_content)

        except Exception as e:
            logger.error(f"Error converting to VTT: {str(e)}")
            return None

    async def get_transcript_url(self, s3_key: str) -> str:
        """Get a presigned URL for accessing the transcript"""
        
        return await self.s3_service.get_presigned_url(
            s3_key,
            expiry_seconds=3600  # 1 hour
        )

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds into WebVTT timestamp"""
        
        time = timedelta(seconds=seconds)
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int(time.microseconds / 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"