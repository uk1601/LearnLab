from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core import deps
from app.models import User
from app.schemas.podcast import UserPodcastAnalytics, PodcastAnalyticsSummary
from app.services.podcast_service import AnalyticsService

router = APIRouter()

@router.get("/analytics/user", response_model=UserPodcastAnalytics)
async def get_user_analytics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    timeframe: Optional[str] = Query(
        None,
        description="Timeframe for analytics (day, week, month, year)",
        regex="^(day|week|month|year)$"
    ),
    analytics_service: AnalyticsService = Depends(deps.get_analytics_service)
):
    """Get user's podcast analytics"""
    
    return await analytics_service.get_user_analytics(
        db,
        current_user.id,
        timeframe
    )

@router.get("/{podcast_id}/analytics", response_model=PodcastAnalyticsSummary)
async def get_podcast_analytics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    podcast_id: UUID,
    analytics_service: AnalyticsService = Depends(deps.get_analytics_service)
):
    """Get analytics for a specific podcast"""
    
    return await analytics_service.get_podcast_analytics(
        db,
        podcast_id
    )