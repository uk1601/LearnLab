from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ....core.deps import get_db, get_current_user
from ....models.user import User
from ....services.quiz_service import QuizService
from ....schemas.quiz import (
    QuizCreate, QuizUpdate, QuizInDB, 
    QuizWithDetails, QuizList
)
from ....core.logger import setup_logger, log_error

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/", response_model=QuizWithDetails)
async def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new quiz"""
    logger.info(f"Creating quiz for user {current_user.id}")
    
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.create_quiz(current_user.id, quiz_data)
        return QuizWithDetails.from_orm(quiz)
        
    except Exception as e:
        log_error(logger, e, {
            'user_id': str(current_user.id),
            'file_id': str(quiz_data.file_id)
        })
        raise HTTPException(status_code=500, detail="Failed to create quiz")

@router.get("/", response_model=QuizList)
async def list_quizzes(
    file_id: UUID = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all quizzes, optionally filtered by file"""
    logger.info(f"Listing quizzes for user {current_user.id}")
    
    try:
        quiz_service = QuizService(db)
        if file_id:
            quizzes = quiz_service.get_file_quizzes(file_id)
        else:
            quizzes = quiz_service.get_user_quizzes(current_user.id)
            
        # Apply pagination
        total = len(quizzes)
        quizzes = quizzes[skip : skip + limit]
        
        return QuizList(
            quizzes=[QuizWithDetails.from_orm(quiz) for quiz in quizzes],
            total=total
        )
        
    except Exception as e:
        log_error(logger, e, {
            'user_id': str(current_user.id),
            'file_id': str(file_id) if file_id else None
        })
        raise HTTPException(status_code=500, detail="Failed to fetch quizzes")

@router.get("/{quiz_id}", response_model=QuizWithDetails)
async def get_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific quiz"""
    logger.info(f"Fetching quiz {quiz_id}")
    
    try:
        quiz_service = QuizService(db)
        quiz = quiz_service.get_quiz(quiz_id)
        
        if not quiz:
            logger.warning(f"Quiz {quiz_id} not found")
            raise HTTPException(status_code=404, detail="Quiz not found")
            
        if not quiz_service.validate_user_access(quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to access unauthorized quiz {quiz_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this quiz")
            
        return QuizWithDetails.from_orm(quiz)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'quiz_id': str(quiz_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to fetch quiz")

@router.put("/{quiz_id}", response_model=QuizWithDetails)
async def update_quiz(
    quiz_id: UUID,
    quiz_data: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update quiz details"""
    logger.info(f"Updating quiz {quiz_id}")
    
    try:
        quiz_service = QuizService(db)
        
        if not quiz_service.validate_user_access(quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to update unauthorized quiz {quiz_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update this quiz")
            
        quiz = quiz_service.update_quiz(quiz_id, quiz_data)
        return QuizWithDetails.from_orm(quiz)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'quiz_id': str(quiz_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to update quiz")


@router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a quiz"""
    logger.info(f"Deleting quiz {quiz_id}")
    
    try:
        quiz_service = QuizService(db)
        
        if not quiz_service.validate_user_access(quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to delete unauthorized quiz {quiz_id}")
            raise HTTPException(status_code=403, detail="Not authorized to delete this quiz")
            
        quiz_service.delete_quiz(quiz_id)
        return {"message": "Quiz deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'quiz_id': str(quiz_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to delete quiz")