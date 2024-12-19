from pydantic import BaseModel, UUID4, HttpUrl, validator, constr
from typing import Optional
from datetime import datetime

class PodcastBase(BaseModel):
    title: constr(min_length=1, max_length=255)
    description: Optional[str] = None
    duration: int  # in seconds
    transcript_status: Optional[str] = "txt_only"

    @validator('duration')
    def duration_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        return v

    @validator('transcript_status')
    def validate_transcript_status(cls, v):
        allowed_statuses = ["txt_only", "vtt_ready", "processing"]
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

class PodcastCreate(PodcastBase):
    file_id: UUID4
    s3_audio_key: str
    s3_transcript_txt_key: str
    s3_transcript_vtt_key: Optional[str] = None

    @validator('s3_audio_key', 's3_transcript_txt_key', 's3_transcript_vtt_key')
    def validate_s3_keys(cls, v):
        if v and not v.startswith('podcasts/'):
            raise ValueError('S3 keys must start with podcasts/')
        return v

class PodcastUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=255)] = None
    description: Optional[str] = None
    transcript_status: Optional[str] = None
    s3_transcript_vtt_key: Optional[str] = None

    @validator('transcript_status')
    def validate_transcript_status(cls, v):
        if v:
            allowed_statuses = ["txt_only", "vtt_ready", "processing"]
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of {allowed_statuses}')
        return v

class PodcastInDB(PodcastBase):
    id: UUID4
    file_id: UUID4
    user_id: UUID4
    s3_audio_key: str
    s3_transcript_txt_key: str
    s3_transcript_vtt_key: Optional[str]
    total_plays: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PodcastWithDetails(PodcastInDB):
    audio_url: Optional[HttpUrl]
    transcript_txt_url: Optional[HttpUrl]
    transcript_vtt_url: Optional[HttpUrl]
    current_progress: Optional[float] = 0.0
    current_speed: Optional[float] = 1.0

    @validator('current_progress')
    def validate_progress(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Progress must be between 0 and 100')
        return v

    @validator('current_speed')
    def validate_speed(cls, v):
        if v is not None and (v < 0.5 or v > 2.0):
            raise ValueError('Speed must be between 0.5 and 2.0')
        return v

    @validator('audio_url', 'transcript_txt_url', 'transcript_vtt_url')
    def validate_urls(cls, v):
        if v:
            allowed_domains = ['s3.amazonaws.com', 'learnlab-files.s3.amazonaws.com']
            if str(v).split('/')[2] not in allowed_domains:
                raise ValueError(f'URL domain must be one of {allowed_domains}')
        return v