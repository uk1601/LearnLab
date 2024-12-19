from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ....core.deps import get_db, get_current_user
from ....models.user import User
from ....services.quiz_service import QuizService, AttemptService, QuestionService
from ....schemas.quiz import (
    AttemptCreate, AttemptUpdate, AttemptInDB,
    ResponseCreate, ResponseInDB
)
from ....core.logger import setup_logger, log_error

logger = setup_logger(__name__)
router = APIRouter()

@router.post("", response_model=AttemptInDB)
async def create_attempt(
    attempt_data: AttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new quiz attempt"""
    logger.info(f"Creating attempt for quiz {attempt_data.quiz_id}")
    
    try:
        # Validate quiz access
        quiz_service = QuizService(db)
        if not quiz_service.validate_user_access(attempt_data.quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted unauthorized quiz {attempt_data.quiz_id}")
            raise HTTPException(status_code=403, detail="Not authorized to attempt this quiz")
            
        attempt_service = AttemptService(db, QuestionService(db))
        attempt = await attempt_service.create_attempt(current_user.id, attempt_data)
        return attempt
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'quiz_id': str(attempt_data.quiz_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to create attempt")

@router.post("/{attempt_id}/responses", response_model=ResponseInDB)
async def submit_response(
    attempt_id: UUID,
    response_data: ResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a response for a question"""
    logger.info(f"Submitting response for attempt {attempt_id}, question {response_data.question_id}")
    
    try:
        attempt_service = AttemptService(db, QuestionService(db))
        
        if not attempt_service.validate_user_access(attempt_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to submit response for unauthorized attempt {attempt_id}")
            raise HTTPException(status_code=403, detail="Not authorized to submit response for this attempt")
            
        response = await attempt_service.submit_response(attempt_id, response_data)
        return response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'attempt_id': str(attempt_id),
            'question_id': str(response_data.question_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to submit response")

@router.patch("/{attempt_id}", response_model=AttemptInDB)
async def complete_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a quiz attempt"""
    logger.info(f"Completing attempt {attempt_id}")
    
    try:
        attempt_service = AttemptService(db, QuestionService(db))
        
        if not attempt_service.validate_user_access(attempt_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to complete unauthorized attempt {attempt_id}")
            raise HTTPException(status_code=403, detail="Not authorized to complete this attempt")
            
        attempt = await attempt_service.complete_attempt(attempt_id)
        return attempt
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'attempt_id': str(attempt_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to complete attempt")

@router.get("/{attempt_id}", response_model=AttemptInDB)
async def get_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a quiz attempt"""
    logger.info(f"Fetching attempt {attempt_id}")
    
    try:
        attempt_service = AttemptService(db, QuestionService(db))
        
        if not attempt_service.validate_user_access(attempt_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to access unauthorized attempt {attempt_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this attempt")
            
        attempt = attempt_service.get_attempt(attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
            
        return attempt
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'attempt_id': str(attempt_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to fetch attempt")

@router.get("/{quiz_id}", response_model=List[AttemptInDB])
async def list_attempts(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all attempts by a user, optionally filtered by quiz"""
    logger.info(f"Listing attempts for user {current_user.id}")
    
    try:
        attempt_service = AttemptService(db, QuestionService(db))
        attempts = attempt_service.get_user_attempts(current_user.id, quiz_id)
        return attempts
        
    except Exception as e:
        log_error(logger, e, {
            'user_id': str(current_user.id),
            'quiz_id': str(quiz_id) if quiz_id else None
        })
        raise HTTPException(status_code=500, detail="Failed to fetch attempts")