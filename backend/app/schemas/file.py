from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class FileBase(BaseModel):
    filename: str
    mime_type: Optional[str] = None

class FileCreate(FileBase):
    file_size: int
    s3_key: str
    user_id: UUID

class File(FileBase):
    id: UUID
    user_id: UUID
    s3_key: str
    file_size: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True

class FileResponse(BaseModel):
    id: UUID
    filename: str
    file_size: int
    mime_type: Optional[str]
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True