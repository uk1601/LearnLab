from typing import Protocol, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
import logging
from datetime import datetime

from app.models.podcast import PodcastProgress, Podcast
from app.schemas.podcast import PodcastProgressCreate, PodcastProgressUpdate

logger = logging.getLogger(__name__)
class IProgressService(Protocol):
    async def update_progress(
        self,
        db: Session,
        user_id: UUID,
        podcast_id: UUID,
        position: int,
        speed: float = 1.0
    ) -> PodcastProgress:
        pass
    
    async def get_progress(
        self,
        db: Session,
        user_id: UUID,
        podcast_id: UUID
    ) -> Optional[PodcastProgress]:
        pass
    
    def calculate_completion(
        self,
        duration: int,
        position: int,
        completed_segments: Optional[List[int]] = None
    ) -> float:
        pass
    
    async def reset_progress(
        self,
        db: Session,
        user_id: UUID,
        podcast_id: UUID
    ) -> None:
        pass
class ProgressService:
    def __init__(self):
        self.SEGMENT_LENGTH = 15  # 15 seconds per segment

    async def update_progress(
        self,
        db: Session,
        user_id: UUID,
        podcast_id: UUID,
        position: int,
        speed: float = 1.0
    ) -> PodcastProgress:
        """Update user's progress for a podcast"""
        
        # Get podcast to validate duration
        podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        # Validate position
        if position < 0 or position > podcast.duration:
            raise HTTPException(
                status_code=400,
                detail=f"Position must be between 0 and {podcast.duration}"
            )

        # Get existing progress or create new
        progress = db.query(PodcastProgress).filter(
            PodcastProgress.user_id == user_id,
            PodcastProgress.podcast_id == podcast_id
        ).first()

        if not progress:
            progress = PodcastProgress(
                user_id=user_id,
                podcast_id=podcast_id,
                completed_segments=[],
                completion_percentage=0.0
            )
            db.add(progress)

        # Update progress
        progress.current_position = position
        progress.playback_speed = speed
        progress.last_played_at = datetime.utcnow()

        # Update completed segments
        current_segment = position // self.SEGMENT_LENGTH
        if current_segment * self.SEGMENT_LENGTH == position and current_segment > 0:
            current_segment -= 1
        if current_segment >= 0:
            completed_segments = set(progress.completed_segments or [])
            completed_segments.add(current_segment)
            progress.completed_segments = sorted(list(completed_segments))

        # Calculate completion percentage
        progress.completion_percentage = self.calculate_completion(
            podcast.duration,
            position,
            progress.completed_segments
        )

        db.commit()
        db.refresh(progress)
        return progress

    async def get_progress(
        self,
        db: Session,
        user_id: UUID,
        podcast_id: UUID
    ) -> Optional[PodcastProgress]:
        """Get user's progress for a podcast"""
        
        return db.query(PodcastProgress).filter(
            PodcastProgress.user_id == user_id,
            PodcastProgress.podcast_id == podcast_id
        ).first()

    def calculate_completion(
        self,
        duration: int,
        position: int,
        completed_segments: Optional[List[int]] = None
    ) -> float:
        """Calculate completion percentage based on position and completed segments"""
        
        if duration == 0:
            return 0.0

        # Calculate total segments
        total_segments = (duration + self.SEGMENT_LENGTH - 1) // self.SEGMENT_LENGTH

        # Count unique completed segments
        unique_segments = set(completed_segments or [])
        completed_count = len(unique_segments)

        # Calculate completion percentage
        completion = (completed_count / total_segments) * 100
        return round(min(completion, 100.0), 2)

    async def reset_progress(
        self,
        db: Session,
        user_id: UUID,
        podcast_id: UUID
    ) -> None:
        """Reset user's progress for a podcast"""
        
        progress = await self.get_progress(db, user_id, podcast_id)
        if progress:
            progress.current_position = 0
            progress.completed_segments = []
            progress.completion_percentage = 0.0
            progress.last_played_at = datetime.utcnow()
            db.commit()