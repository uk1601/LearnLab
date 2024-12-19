from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core import deps
from app.models import User
from app.models.podcast import PodcastProgress
from app.schemas.podcast import PodcastProgressCreate, PodcastProgressUpdate, PodcastProgressInDB
from app.services.podcast_service import ProgressService, AnalyticsService

router = APIRouter()

@router.patch("/{podcast_id}/progress", response_model=PodcastProgressInDB)
async def update_progress(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    podcast_id: UUID,
    position: int = Query(..., ge=0),
    speed: float = Query(1.0, ge=0.5, le=2.0),
    progress_service: ProgressService = Depends(deps.get_progress_service),
    analytics_service: AnalyticsService = Depends(deps.get_analytics_service)
):
    """Update podcast progress and playback position"""
    
    # Update progress
    progress = await progress_service.update_progress(
        db,
        current_user.id,
        podcast_id,
        position,
        speed
    )
    
    # Update analytics for this session
    await analytics_service.update_analytics(
        db,
        current_user.id,
        podcast_id,
        15,  # Session duration (progress update interval)
        speed
    )
    
    return progress

@router.get("/{podcast_id}/progress", response_model=PodcastProgressInDB)
async def get_progress(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    podcast_id: UUID,
    progress_service: ProgressService = Depends(deps.get_progress_service)
):
    """Get user's progress for a podcast"""
    
    progress = await progress_service.get_progress(
        db,
        current_user.id,
        podcast_id
    )
    
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found")
        
    return progress

@router.post("/{podcast_id}/reset-progress")
async def reset_progress(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    podcast_id: UUID,
    progress_service: ProgressService = Depends(deps.get_progress_service)
):
    """Reset progress for a podcast"""
    
    await progress_service.reset_progress(
        db,
        current_user.id,
        podcast_id
    )
    
    return {"message": "Progress reset successfully"}