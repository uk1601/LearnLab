from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core import deps
from app.models import User
from app.models.podcast import Podcast
from app.schemas.podcast import (
    PodcastCreate,
    PodcastUpdate,
    PodcastInDB,
    PodcastWithDetails
)
from app.services.podcast_service import (
    AudioService,
    TranscriptService,
    S3Service
)

router = APIRouter()

@router.post("/", response_model=PodcastInDB)
async def create_podcast(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    file_id: UUID = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    audio_file: UploadFile = File(...),
    transcript_file: UploadFile = File(...),
    audio_service: AudioService = Depends(deps.get_audio_service),
    transcript_service: TranscriptService = Depends(deps.get_transcript_service)
):
    """Create a new podcast with audio and transcript"""    
    # Process audio file
    s3_audio_key, duration = await audio_service.upload_podcast(
        audio_file, 
        current_user.id,
        validate_duration=True
    )

    # Process transcript
    transcript_keys = await transcript_service.process_transcript(
        transcript_file,
        current_user.id
    )

    # Create podcast
    podcast = Podcast(
        file_id=file_id,
        user_id=current_user.id,
        title=title,
        description=description,
        duration=duration,
        s3_audio_key=s3_audio_key,
        s3_transcript_txt_key=transcript_keys['txt_key'],
        s3_transcript_vtt_key=transcript_keys.get('vtt_key'),
        transcript_status='vtt_ready' if 'vtt_key' in transcript_keys else 'txt_only'
    )
    
    db.add(podcast)
    db.commit()
    db.refresh(podcast)
    
    return podcast

@router.get("/{podcast_id}", response_model=PodcastWithDetails)
async def get_podcast(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    podcast_id: UUID,
    audio_service: AudioService = Depends(deps.get_audio_service),
    transcript_service: TranscriptService = Depends(deps.get_transcript_service)
):
    """Get podcast details with streaming URLs"""
    
    podcast = db.query(Podcast).filter(
        Podcast.id == podcast_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Get current progress
    progress = podcast.progress[0] if podcast.progress else None
    current_progress = progress.completion_percentage if progress else 0.0
    current_speed = progress.playback_speed if progress else 1.0
    
    # Generate URLs
    audio_url = await audio_service.get_streaming_url(podcast.s3_audio_key)
    transcript_txt_url = await transcript_service.get_transcript_url(
        podcast.s3_transcript_txt_key
    )
    transcript_vtt_url = None
    if podcast.s3_transcript_vtt_key:
        transcript_vtt_url = await transcript_service.get_transcript_url(
            podcast.s3_transcript_vtt_key
        )

    return {
        **podcast.__dict__,
        'audio_url': audio_url,
        'transcript_txt_url': transcript_txt_url,
        'transcript_vtt_url': transcript_vtt_url,
        'current_progress': current_progress,
        'current_speed': current_speed
    }

@router.get("/", response_model=List[PodcastInDB])
async def list_podcasts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """List user's podcasts with pagination"""
    
    podcasts = db.query(Podcast).filter(
        Podcast.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return podcasts

@router.patch("/{podcast_id}", response_model=PodcastInDB)
async def update_podcast(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    podcast_id: UUID,
    update_data: PodcastUpdate,
    transcript_service: TranscriptService = Depends(deps.get_transcript_service)
):
    """Update podcast details"""
    
    podcast = db.query(Podcast).filter(
        Podcast.id == podcast_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(podcast, field, value)

    db.commit()
    db.refresh(podcast)
    return podcast

@router.delete("/{podcast_id}")
async def delete_podcast(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    podcast_id: UUID,
    s3_service: S3Service = Depends(deps.get_s3_service)
):
    """Delete a podcast and its associated files"""
    
    podcast = db.query(Podcast).filter(
        Podcast.id == podcast_id,
        Podcast.user_id == current_user.id
    ).first()
    
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Delete S3 files
    try:
        await s3_service.delete_file(podcast.s3_audio_key)
        await s3_service.delete_file(podcast.s3_transcript_txt_key)
        if podcast.s3_transcript_vtt_key:
            await s3_service.delete_file(podcast.s3_transcript_vtt_key)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete podcast files: {str(e)}"
        )

    # Delete from database
    db.delete(podcast)
    db.commit()
    
    return {"message": "Podcast deleted successfully"}