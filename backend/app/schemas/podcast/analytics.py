from pydantic import BaseModel, UUID4, validator
from typing import Optional
from datetime import datetime, date

class PodcastAnalyticsBase(BaseModel):
    date: date
    total_time_listened: int = 0
    average_speed: float = 1.0
    number_of_sessions: int = 0
    completion_rate: float = 0.0

    @validator('total_time_listened')
    def validate_time_listened(cls, v):
        if v < 0:
            raise ValueError('Total time listened cannot be negative')
        return v

    @validator('average_speed')
    def validate_speed(cls, v):
        if v < 0.5 or v > 2.0:
            raise ValueError('Average speed must be between 0.5 and 2.0')
        return v

    @validator('number_of_sessions')
    def validate_sessions(cls, v):
        if v < 0:
            raise ValueError('Number of sessions cannot be negative')
        return v

    @validator('completion_rate')
    def validate_completion(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Completion rate must be between 0 and 100')
        return v

class PodcastAnalyticsCreate(PodcastAnalyticsBase):
    podcast_id: UUID4

class PodcastAnalyticsInDB(PodcastAnalyticsBase):
    id: UUID4
    user_id: UUID4
    podcast_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserPodcastAnalytics(BaseModel):
    total_podcasts: int
    total_time_listened: int
    average_completion_rate: float
    average_speed: float
    learning_streak: int

    @validator('average_completion_rate')
    def validate_completion_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Average completion rate must be between 0 and 100')
        return v

    @validator('average_speed')
    def validate_speed(cls, v):
        if v < 0.5 or v > 2.0:
            raise ValueError('Average speed must be between 0.5 and 2.0')
        return v

class PodcastAnalyticsSummary(BaseModel):
    unique_listeners: int
    total_plays: int
    average_completion: float
    engagement_score: float
    average_speed: float

    @validator('average_completion')
    def validate_completion(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Average completion must be between 0 and 100')
        return v

    @validator('engagement_score')
    def validate_engagement(cls, v):
        if v < 0:
            raise ValueError('Engagement score cannot be negative')
        return v

    @validator('average_speed')
    def validate_speed(cls, v):
        if v < 0.5 or v > 2.0:
            raise ValueError('Average speed must be between 0.5 and 2.0')
        return v