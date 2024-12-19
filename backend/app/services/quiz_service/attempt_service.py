from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ...core.logger import setup_logger, log_error
from ...models.quiz import QuizAttempt, QuestionResponse, Question
from ...schemas.quiz import AttemptCreate, AttemptUpdate, ResponseCreate, ResponseUpdate

logger = setup_logger(__name__)

class AttemptService:
    def __init__(self, db: Session, question_service):
        self.db = db
        self.question_service = question_service

    async def create_attempt(self, user_id: UUID, attempt_data: AttemptCreate) -> QuizAttempt:
        """Create a new quiz attempt"""
        logger.info(f"Creating attempt for user {user_id}, quiz {attempt_data.quiz_id}")
        
        try:
            # Check for unfinished attempts
            existing_attempt = self.db.query(QuizAttempt).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == attempt_data.quiz_id,
                QuizAttempt.status == 'in_progress'
            ).first()

            if existing_attempt:
                logger.debug(f"Found existing attempt {existing_attempt.id}")
                return existing_attempt

            # Create new attempt
            attempt = QuizAttempt(
                user_id=user_id,
                quiz_id=attempt_data.quiz_id,
                status='in_progress'
            )
            self.db.add(attempt)
            self.db.commit()
            self.db.refresh(attempt)
            
            logger.debug(f"Created new attempt {attempt.id}")
            return attempt
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'user_id': str(user_id),
                'quiz_id': str(attempt_data.quiz_id),
                'operation': 'create_attempt'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create attempt")

    async def submit_response(self, attempt_id: UUID, response_data: ResponseCreate) -> QuestionResponse:
        """Submit a response for a question"""
        logger.info(f"Submitting response for attempt {attempt_id}, question {response_data.question_id}")
        
        try:
            # Check if response already exists
            existing_response = self.db.query(QuestionResponse).filter(
                QuestionResponse.attempt_id == attempt_id,
                QuestionResponse.question_id == response_data.question_id
            ).first()

            if existing_response:
                logger.warning(f"Response already exists for question {response_data.question_id}")
                raise HTTPException(status_code=400, detail="Response already submitted")

            # Check answer
            is_correct, confidence_score = await self.question_service.check_answer(
                response_data.question_id,
                response_data.response
            )

            # Create response
            response = QuestionResponse(
                attempt_id=attempt_id,
                question_id=response_data.question_id,
                response=response_data.response,
                is_correct=is_correct,
                confidence_score=confidence_score,
                time_taken=response_data.time_taken
            )
            self.db.add(response)
            self.db.commit()
            self.db.refresh(response)
            
            logger.debug(f"Submitted response {response.id}")
            return response
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'attempt_id': str(attempt_id),
                'question_id': str(response_data.question_id),
                'operation': 'submit_response'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to submit response")

    async def complete_attempt(self, attempt_id: UUID) -> QuizAttempt:
        """Complete a quiz attempt and calculate score"""
        logger.info(f"Completing attempt {attempt_id}")
        
        try:
            attempt = self.get_attempt(attempt_id)
            if not attempt:
                raise HTTPException(status_code=404, detail="Attempt not found")

            if attempt.status == 'completed':
                logger.warning(f"Attempt {attempt_id} already completed")
                return attempt

            # Calculate score
            total_questions = self.db.query(Question).filter(
                Question.quiz_id == attempt.quiz_id,
                Question.is_active == True
            ).count()

            if total_questions == 0:
                raise HTTPException(status_code=400, detail="Quiz has no active questions")

            correct_answers = self.db.query(QuestionResponse).filter(
                QuestionResponse.attempt_id == attempt_id,
                QuestionResponse.is_correct == True
            ).count()

            # Update attempt
            attempt.score = (correct_answers / total_questions) * 100
            attempt.status = 'completed'
            attempt.end_time = datetime.utcnow()

            self.db.commit()
            self.db.refresh(attempt)
            
            logger.debug(f"Completed attempt {attempt_id} with score {attempt.score}")
            return attempt
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'attempt_id': str(attempt_id),
                'operation': 'complete_attempt'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to complete attempt")

    def get_attempt(self, attempt_id: UUID) -> Optional[QuizAttempt]:
        """Get attempt by ID"""
        logger.debug(f"Fetching attempt {attempt_id}")
        
        try:
            attempt = self.db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
            if not attempt:
                logger.warning(f"Attempt {attempt_id} not found")
                return None
            return attempt
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'attempt_id': str(attempt_id),
                'operation': 'get_attempt'
            })
            raise HTTPException(status_code=500, detail="Failed to fetch attempt")

    def get_user_attempts(self, user_id: UUID, quiz_id: Optional[UUID] = None) -> List[QuizAttempt]:
        """Get all attempts by a user, optionally filtered by quiz"""
        logger.debug(f"Fetching attempts for user {user_id}")
        
        try:
            query = self.db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)
            if quiz_id:
                query = query.filter(QuizAttempt.quiz_id == quiz_id)
            return query.order_by(QuizAttempt.created_at.desc()).all()
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'user_id': str(user_id),
                'quiz_id': str(quiz_id) if quiz_id else None,
                'operation': 'get_user_attempts'
            })
            raise HTTPException(status_code=500, detail="Failed to fetch attempts")

    def validate_user_access(self, attempt_id: UUID, user_id: UUID) -> bool:
        """Validate if user has access to the attempt"""
        logger.debug(f"Validating access for user {user_id} to attempt {attempt_id}")
        
        try:
            attempt = self.get_attempt(attempt_id)
            if not attempt:
                return False
            return attempt.user_id == user_id
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'attempt_id': str(attempt_id),
                'user_id': str(user_id),
                'operation': 'validate_user_access'
            })
            return False