from pydantic import BaseModel, UUID4, validator, conlist
from typing import Optional, List
from datetime import datetime

class PodcastProgressBase(BaseModel):
    current_position: int = 0
    playback_speed: float = 1.0
    completed_segments: List[int] = []
    completion_percentage: float = 0.0

    @validator('current_position')
    def validate_position(cls, v):
        if v < 0:
            raise ValueError('Position cannot be negative')
        return v

    @validator('playback_speed')
    def validate_speed(cls, v):
        if v < 0.5 or v > 2.0:
            raise ValueError('Playback speed must be between 0.5 and 2.0')
        return v

    @validator('completed_segments')
    def validate_segments(cls, v):
        if not all(isinstance(x, int) and x >= 0 for x in v):
            raise ValueError('Segments must be non-negative integers')
        return sorted(list(set(v)))  # Remove duplicates and sort

    @validator('completion_percentage')
    def validate_completion(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Completion percentage must be between 0 and 100')
        return v

class PodcastProgressCreate(PodcastProgressBase):
    podcast_id: UUID4

class PodcastProgressUpdate(BaseModel):
    current_position: Optional[int] = None
    playback_speed: Optional[float] = None
    completed_segments: Optional[List[int]] = None

    @validator('current_position')
    def validate_position(cls, v):
        if v is not None and v < 0:
            raise ValueError('Position cannot be negative')
        return v

    @validator('playback_speed')
    def validate_speed(cls, v):
        if v is not None and (v < 0.5 or v > 2.0):
            raise ValueError('Playback speed must be between 0.5 and 2.0')
        return v

    @validator('completed_segments')
    def validate_segments(cls, v):
        if v is not None:
            if not all(isinstance(x, int) and x >= 0 for x in v):
                raise ValueError('Segments must be non-negative integers')
            return sorted(list(set(v)))  # Remove duplicates and sort
        return v

class PodcastProgressInDB(PodcastProgressBase):
    id: UUID4
    user_id: UUID4
    podcast_id: UUID4
    last_played_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True