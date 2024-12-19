from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ...core.logger import setup_logger, log_error
from ...models.quiz import Quiz, Question, QuestionConcept, MultipleChoiceOption, SubjectiveAnswer
from ...schemas.quiz import QuizCreate, QuizUpdate, QuestionCreate

logger = setup_logger(__name__)

class QuizService:
    def __init__(self, db: Session):
        self.db = db

    def create_quiz(self, user_id: UUID, quiz_data: QuizCreate) -> Quiz:
        """Create a new quiz"""
        logger.info(f"Creating quiz for user {user_id}, file {quiz_data.file_id}")
        
        try:
            quiz = Quiz(
                user_id=user_id,
                file_id=quiz_data.file_id,
                title=quiz_data.title,
                description=quiz_data.description
            )
            self.db.add(quiz)
            self.db.commit()
            self.db.refresh(quiz)
            
            logger.debug(f"Successfully created quiz {quiz.id}")
            return quiz
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'user_id': str(user_id),
                'operation': 'create_quiz'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create quiz")

    def get_quiz(self, quiz_id: UUID) -> Optional[Quiz]:
        """Get quiz by ID"""
        logger.debug(f"Fetching quiz {quiz_id}")
        
        try:
            quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
            if not quiz:
                logger.warning(f"Quiz {quiz_id} not found")
                return None
            return quiz
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'quiz_id': str(quiz_id),
                'operation': 'get_quiz'
            })
            raise HTTPException(status_code=500, detail="Database error occurred")

    def get_file_quizzes(self, file_id: UUID) -> List[Quiz]:
        """Get all quizzes for a file"""
        logger.debug(f"Fetching quizzes for file {file_id}")
        
        try:
            return self.db.query(Quiz).filter(
                Quiz.file_id == file_id,
                Quiz.is_active == True
            ).all()
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'file_id': str(file_id),
                'operation': 'get_file_quizzes'
            })
            raise HTTPException(status_code=500, detail="Failed to fetch quizzes")

    def get_user_quizzes(self, user_id: UUID) -> List[Quiz]:
        """Get all quizzes created by a user"""
        logger.debug(f"Fetching quizzes for user {user_id}")
        
        try:
            return self.db.query(Quiz).filter(
                Quiz.user_id == user_id,
                Quiz.is_active == True
            ).all()
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'user_id': str(user_id),
                'operation': 'get_user_quizzes'
            })
            raise HTTPException(status_code=500, detail="Failed to fetch quizzes")

    def update_quiz(self, quiz_id: UUID, quiz_data: QuizUpdate) -> Quiz:
        """Update quiz details"""
        logger.info(f"Updating quiz {quiz_id}")
        
        try:
            quiz = self.get_quiz(quiz_id)
            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")

            for key, value in quiz_data.dict(exclude_unset=True).items():
                setattr(quiz, key, value)

            self.db.commit()
            self.db.refresh(quiz)
            
            logger.debug(f"Successfully updated quiz {quiz_id}")
            return quiz
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'quiz_id': str(quiz_id),
                'operation': 'update_quiz'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update quiz")

    def delete_quiz(self, quiz_id: UUID):
        """Soft delete a quiz"""
        logger.info(f"Deleting quiz {quiz_id}")
        
        try:
            quiz = self.get_quiz(quiz_id)
            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")

            # Soft delete
            quiz.is_active = False
            self.db.commit()
            
            logger.debug(f"Successfully deleted quiz {quiz_id}")
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'quiz_id': str(quiz_id),
                'operation': 'delete_quiz'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete quiz")

    def validate_user_access(self, quiz_id: UUID, user_id: UUID) -> bool:
        """Validate if user has access to the quiz"""
        logger.debug(f"Validating access for user {user_id} to quiz {quiz_id}")
        
        try:
            quiz = self.get_quiz(quiz_id)
            if not quiz:
                return False
            return quiz.user_id == user_id
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'quiz_id': str(quiz_id),
                'user_id': str(user_id),
                'operation': 'validate_user_access'
            })
            return False