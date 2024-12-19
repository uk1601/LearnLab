from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ....core.deps import get_db, get_current_user
from ....models.user import User
from ....services.quiz_service import QuizService, QuestionService
from ....schemas.quiz import (
    QuestionCreate, QuestionUpdate, QuestionInDB,
    QuestionWithOptions, QuestionWithAnswer
)
from ....core.logger import setup_logger, log_error

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/{quiz_id}", response_model=List[QuestionWithOptions | QuestionWithAnswer])
async def get_questions(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all questions for a quiz"""
    logger.info(f"Fetching all questions for quiz {quiz_id}")
    
    try:
        quiz_service = QuizService(db)
        if not quiz_service.validate_user_access(quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to access unauthorized questions for quiz {quiz_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access these questions")
            
        question_service = QuestionService(db)
        questions = question_service.get_quiz_questions(quiz_id)
        for question in questions:
            db.refresh(question)
            
        # Return appropriate schema based on question type
        question_schemas = []
        for question in questions:
            print(question.question_type)            
            if question.question_type == 'multiple_choice':
                question_schemas.append(QuestionWithOptions.from_orm(question))
            else:
                question_schemas.append(QuestionWithAnswer.from_orm(question))
                
        return question_schemas
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'quiz_id': str(quiz_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to fetch questions")

@router.get("/{question_id}", response_model=QuestionWithOptions | QuestionWithAnswer)
async def get_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific question"""
    logger.info(f"Fetching question {question_id}")
    
    try:
        question_service = QuestionService(db)
        question = question_service.get_question(question_id)        
        if not question:
            logger.warning(f"Question {question_id} not found")
            raise HTTPException(status_code=404, detail="Question not found")
            
        # Validate access through quiz
        quiz_service = QuizService(db)
        if not quiz_service.validate_user_access(question.quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to access unauthorized question {question_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this question")
            
        # Return appropriate schema based on question type
        if question.question_type == 'multiple_choice':
            return QuestionWithOptions.from_orm(question)
        else:
            return QuestionWithAnswer.from_orm(question)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'question_id': str(question_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to fetch question")

@router.put("/{question_id}", response_model=QuestionInDB)
async def update_question(
    question_id: UUID,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update question details"""
    logger.info(f"Updating question {question_id}")
    
    try:
        question_service = QuestionService(db)
        question = question_service.get_question(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
            
        # Validate access through quiz
        quiz_service = QuizService(db)
        if not quiz_service.validate_user_access(question.quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to update unauthorized question {question_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update this question")
            
        return question_service.update_question(question_id, question_data)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'question_id': str(question_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to update question")

@router.delete("/{question_id}")
async def delete_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a question"""
    logger.info(f"Deleting question {question_id}")
    
    try:
        question_service = QuestionService(db)
        question = question_service.get_question(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
            
        # Validate access through quiz
        quiz_service = QuizService(db)
        if not quiz_service.validate_user_access(question.quiz_id, current_user.id):
            logger.warning(f"User {current_user.id} attempted to delete unauthorized question {question_id}")
            raise HTTPException(status_code=403, detail="Not authorized to delete this question")
            
        question_service.delete_question(question_id)
        return {"message": "Question deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'question_id': str(question_id),
            'user_id': str(current_user.id)
        })
        raise HTTPException(status_code=500, detail="Failed to delete question")