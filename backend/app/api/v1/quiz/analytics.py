from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ....core.deps import get_db, get_current_user
from ....models.user import User
from ....services.quiz_service import QuizService, AnalyticsService
from ....schemas.quiz import FileQuizStats, QuizAnalytics, QuizProgressStats
from ....core.logger import setup_logger, log_error

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/files/{file_id}", response_model=FileQuizStats)
async def get_file_quiz_stats(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quiz statistics for a file"""
    logger.info(f"Generating quiz stats for file {file_id}")
    
    try:
        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_file_quiz_stats(file_id)
        return stats
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'file_id': str(file_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to generate file statistics")

@router.get("/quizzes/{quiz_id}", response_model=QuizAnalytics)
async def get_quiz_analytics(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analytics for a quiz"""
    logger.info(f"Generating analytics for quiz {quiz_id}")
    
    try:
        # Validate access
        quiz_service = QuizService(db)
        if not quiz_service.validate_user_access(quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to access analytics for unauthorized quiz {quiz_id}")
            raise HTTPException(status_code=403, detail="Not authorized to view these analytics")
            
        analytics_service = AnalyticsService(db)
        analytics = analytics_service.get_quiz_analytics(quiz_id)
        return analytics
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'quiz_id': str(quiz_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to generate quiz analytics")

@router.get("/quizzes/{quiz_id}/progress", response_model=QuizProgressStats)
async def get_quiz_progress_stats(
    quiz_id: UUID,
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quiz progress statistics over time"""
    logger.info(f"Generating progress stats for quiz {quiz_id}")
    
    try:
        # Validate access
        quiz_service = QuizService(db)
        if not quiz_service.validate_user_access(quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to access progress stats for unauthorized quiz {quiz_id}")
            raise HTTPException(status_code=403, detail="Not authorized to view these statistics")
            
        # Only allow viewing other users' stats with proper authorization
        if user_id and user_id != current_user.id:
            # TODO: Add proper authorization check for viewing other users' stats
            raise HTTPException(status_code=403, detail="Not authorized to view other users' statistics")
            
        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_quiz_progress_stats(quiz_id, user_id or current_user.id)
        return stats
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'quiz_id': str(quiz_id),
            'user_id': str(current_user.id),
            'target_user_id': str(user_id) if user_id else None
        })
        raise HTTPException(status_code=500, detail="Failed to generate progress statistics")