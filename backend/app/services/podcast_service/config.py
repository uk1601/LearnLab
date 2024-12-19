from pydantic import BaseSettings
from typing import List
from functools import lru_cache

class PodcastServiceSettings(BaseSettings):
    # Audio settings
    ALLOWED_AUDIO_FORMATS: List[str] = ["mp3", "wav", "m4a", "ogg"]
    MAX_AUDIO_SIZE_MB: int = 500
    MIN_DURATION_SECONDS: int = 30
    MAX_DURATION_SECONDS: int = 4 * 60 * 60  # 4 hours
    
    # Transcript settings
    ALLOWED_TRANSCRIPT_FORMATS: List[str] = ["txt", "vtt"]
    MAX_TRANSCRIPT_SIZE_MB: int = 10
    
    # Progress settings
    SEGMENT_LENGTH_SECONDS: int = 15
    PROGRESS_UPDATE_INTERVAL: int = 15  # seconds
    
    # Playback settings
    MIN_PLAYBACK_SPEED: float = 0.5
    MAX_PLAYBACK_SPEED: float = 2.0
    ALLOWED_PLAYBACK_SPEEDS: List[float] = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    
    # Analytics settings
    MAX_SESSION_DURATION: int = 8 * 60 * 60  # 8 hours
    MIN_SESSION_DURATION: int = 5  # 5 seconds
    
    # S3 settings
    S3_AUDIO_PREFIX: str = "podcasts/"
    S3_TRANSCRIPT_PREFIX: str = "transcripts/"
    URL_EXPIRY_SECONDS: int = 3600  # 1 hour

    class Config:
        case_sensitive = True

@lru_cache()
def get_podcast_settings() -> PodcastServiceSettings:
    """Get cached podcast service settings"""
    return PodcastServiceSettings()

# Create a global settings instance
podcast_settings = get_podcast_settings()