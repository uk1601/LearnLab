from typing import Protocol, Optional, Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
import logging
from datetime import datetime, date
from sqlalchemy import func, and_
from sqlalchemy import distinct
from app.models.podcast import PodcastAnalytics, Podcast, PodcastProgress
from app.schemas.podcast import (
    PodcastAnalyticsCreate,
    UserPodcastAnalytics,
    PodcastAnalyticsSummary
)

logger = logging.getLogger(__name__)


class IAnalyticsService(Protocol):
    async def update_analytics(
        self,
        db: Session,
        user_id: UUID,
        podcast_id: UUID,
        session_duration: int,
        speed: float
    ) -> PodcastAnalytics:
        pass
    
    async def get_user_analytics(
        self,
        db: Session,
        user_id: UUID,
        timeframe: Optional[str] = None
    ) -> UserPodcastAnalytics:
        pass
    
    async def get_podcast_analytics(
        self,
        db: Session,
        podcast_id: UUID
    ) -> PodcastAnalyticsSummary:
        pass
    
    async def _calculate_learning_streak(
        self,
        db: Session,
        user_id: UUID
    ) -> int:
        pass


class AnalyticsService:
    async def update_analytics(
        self,
        db: Session,
        user_id: UUID,
        podcast_id: UUID,
        session_duration: int,
        speed: float
    ) -> PodcastAnalytics:
        """Update analytics for a podcast session"""
        
        today = date.today()
        
        # Get or create analytics for today
        analytics = db.query(PodcastAnalytics).filter(
            PodcastAnalytics.user_id == user_id,
            PodcastAnalytics.podcast_id == podcast_id,
            PodcastAnalytics.date == today
        ).first()

        if not analytics:
            analytics = PodcastAnalytics(
                user_id=user_id,
                podcast_id=podcast_id,
                date=today,
                total_time_listened=0,
                average_speed=speed,
                number_of_sessions=0,
                completion_rate=0.0
            )
            db.add(analytics)

        # Update analytics
        analytics.total_time_listened += session_duration
        analytics.number_of_sessions += 1
        
        # Update average speed
        analytics.average_speed = (
            (analytics.average_speed * (analytics.number_of_sessions - 1) + speed) /
            analytics.number_of_sessions
        )

        # Get current progress to update completion rate
        progress = db.query(PodcastProgress).filter(
            PodcastProgress.user_id == user_id,
            PodcastProgress.podcast_id == podcast_id
        ).first()

        if progress:
            analytics.completion_rate = progress.completion_percentage

        db.commit()
        db.refresh(analytics)
        return analytics

    async def get_user_analytics(
        self,
        db: Session,
        user_id: UUID,
        timeframe: Optional[str] = None
    ) -> UserPodcastAnalytics:
        """Get analytics summary for a user"""
        
        # Base query
        query = db.query(
            func.count(distinct(PodcastAnalytics.podcast_id)).label("total_podcasts"),
            func.sum(PodcastAnalytics.total_time_listened).label("total_time_listened"),
            func.avg(PodcastAnalytics.completion_rate).label("avg_completion_rate"),
            func.avg(PodcastAnalytics.average_speed).label("avg_speed")
        ).filter(PodcastAnalytics.user_id == user_id)

        # Apply timeframe filter
        if timeframe:
            if timeframe == "week":
                query = query.filter(
                    PodcastAnalytics.date >= func.date_trunc('week', func.current_date())
                )
            elif timeframe == "month":
                query = query.filter(
                    PodcastAnalytics.date >= func.date_trunc('month', func.current_date())
                )
            elif timeframe == "year":
                query = query.filter(
                    PodcastAnalytics.date >= func.date_trunc('year', func.current_date())
                )

        result = query.first()

        # Calculate learning streak
        streak = await self._calculate_learning_streak(db, user_id)

        return UserPodcastAnalytics(
            total_podcasts=result[0] or 0,
            total_time_listened=result[1] or 0,
            average_completion_rate=result[2] or 0.0,
            average_speed=result[3] or 1.0,
            learning_streak=streak
        )

    async def get_podcast_analytics(
        self,
        db: Session,
        podcast_id: UUID
    ) -> PodcastAnalyticsSummary:
        """Get analytics summary for a podcast"""
        
        result = db.query(
            func.count(distinct(PodcastAnalytics.user_id)).label("unique_listeners"),
            func.avg(PodcastAnalytics.completion_rate).label("avg_completion"),
            func.avg(PodcastAnalytics.average_speed).label("avg_speed")
        ).filter(
            PodcastAnalytics.podcast_id == podcast_id
        ).first()

        # Get total plays from podcast table
        total_plays = db.query(Podcast.total_plays).filter(
            Podcast.id == podcast_id
        ).scalar() or 0

        # Calculate engagement score
        engagement_score = (
            (result[0] or 0) * (result[1] or 0)
        ) / 100.0 if result[0] and result[1] else 0.0

        return PodcastAnalyticsSummary(
            unique_listeners=result[0] or 0,
            total_plays=total_plays,
            average_completion=result[1] or 0.0,
            average_speed=result[2] or 1.0,
            engagement_score=engagement_score
        )

    async def _calculate_learning_streak(self, db: Session, user_id: UUID) -> int:
        """Calculate user's current learning streak in days"""
        
        streak = 0
        current_date = date.today()

        while True:
            has_activity = db.query(PodcastAnalytics).filter(
                PodcastAnalytics.user_id == user_id,
                PodcastAnalytics.date == current_date,
                PodcastAnalytics.total_time_listened > 0
            ).first() is not None

            if not has_activity:
                break

            streak += 1
            current_date = current_date - timedelta(days=1)

        return streak