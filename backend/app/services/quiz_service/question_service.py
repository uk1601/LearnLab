from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.orm import selectinload


from ...core.logger import setup_logger, log_error
from ...models.quiz import (
    Question, QuestionConcept, MultipleChoiceOption, 
    SubjectiveAnswer, QuestionResponse
)
from ...schemas.quiz import QuestionCreate, QuestionUpdate

logger = setup_logger(__name__)

class QuestionService:
    def __init__(self, db: Session):
        self.db = db

    async def create_question(self, quiz_id: UUID, question_data: QuestionCreate) -> Question:
        """Create a new question with associated concepts and answers"""
        logger.info(f"Creating question for quiz {quiz_id}")
        
        try:
            # Create question
            question = Question(
                quiz_id=quiz_id,
                question_type=question_data.question_type,
                content=question_data.content,
                explanation=question_data.explanation
            )
            self.db.add(question)
            self.db.flush()  # Get question ID without committing

            # Add concepts
            for concept in question_data.concepts:
                concept_obj = QuestionConcept(
                    question_id=question.id,
                    concept=concept
                )
                self.db.add(concept_obj)

            # Add answers based on question type
            if question_data.question_type == 'multiple_choice':
                for option in question_data.options:
                    option_obj = MultipleChoiceOption(
                        question_id=question.id,
                        content=option.content,
                        is_correct=option.is_correct
                    )
                    self.db.add(option_obj)
            else:  # subjective
                answer_obj = SubjectiveAnswer(
                    question_id=question.id,
                    answer=question_data.answer.answer
                )
                self.db.add(answer_obj)

            self.db.commit()
            self.db.refresh(question)
            
            logger.debug(f"Successfully created question {question.id}")
            return question
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'quiz_id': str(quiz_id),
                'operation': 'create_question'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create question")

    def get_question(self, question_id: UUID) -> Optional[Question]:
        """Get question by ID"""
        logger.debug(f"Fetching question {question_id}")
        
        try:
            question = self.db.query(Question).filter(Question.id == question_id).first()
            if not question:
                logger.warning(f"Question {question_id} not found")
                return None
            return question
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'question_id': str(question_id),
                'operation': 'get_question'
            })
            raise HTTPException(status_code=500, detail="Failed to fetch question")

    async def check_answer(self, question_id: UUID, response: str) -> tuple[bool, Optional[float]]:
        """
        Check if an answer is correct and return confidence score for subjective answers
        Returns: (is_correct, confidence_score)
        """
        logger.info(f"Checking answer for question {question_id}")
        
        try:
            question = self.get_question(question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")

            if question.question_type == 'multiple_choice':
                correct_option = self.db.query(MultipleChoiceOption).filter(
                    MultipleChoiceOption.question_id == question_id,
                    MultipleChoiceOption.is_correct == True
                ).first()
                return response.strip() == correct_option.content.strip(), None
            else:
                # TODO: Implement LLM-based answer checking
                # For now, implement basic string matching
                expected_answer = self.db.query(SubjectiveAnswer).filter(
                    SubjectiveAnswer.question_id == question_id
                ).first()
                
                confidence_score = self._calculate_answer_similarity(
                    response, 
                    expected_answer.answer
                )
                return confidence_score > 0.8, confidence_score
                
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'question_id': str(question_id),
                'operation': 'check_answer'
            })
            raise HTTPException(status_code=500, detail="Failed to check answer")

    def _calculate_answer_similarity(self, response: str, expected: str) -> float:
        """
        Calculate similarity between response and expected answer
        Returns a score between 0 and 1
        TODO: Replace with LLM-based similarity check
        """
        # Basic implementation for now
        response_words = set(response.lower().split())
        expected_words = set(expected.lower().split())
        
        if not expected_words:
            return 0.0
            
        common_words = response_words.intersection(expected_words)
        return len(common_words) / len(expected_words)

    def update_question(self, question_id: UUID, question_data: QuestionUpdate) -> Question:
        """Update question details"""
        logger.info(f"Updating question {question_id}")
        
        try:
            question = self.get_question(question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")

            for key, value in question_data.dict(exclude_unset=True).items():
                setattr(question, key, value)

            self.db.commit()
            self.db.refresh(question)
            
            logger.debug(f"Successfully updated question {question_id}")
            return question
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'question_id': str(question_id),
                'operation': 'update_question'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update question")

    def delete_question(self, question_id: UUID):
        """Soft delete a question"""
        logger.info(f"Deleting question {question_id}")
        
        try:
            question = self.get_question(question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")

            question.is_active = False
            self.db.commit()
            
            logger.debug(f"Successfully deleted question {question_id}")
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'question_id': str(question_id),
                'operation': 'delete_question'
            })
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete question")

    def get_quiz_questions(self, quiz_id: UUID) -> List[Question]:
        """Get all questions for a quiz"""
        logger.debug(f"Fetching questions for quiz {quiz_id}")
        
        try:
            return self.db.query(Question).filter(
                Question.quiz_id == quiz_id,
                Question.is_active == True
            ).options(
                selectinload(Question.concepts),
                selectinload(Question.multiple_choice_options),
                selectinload(Question.subjective_answer)).all()
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'quiz_id': str(quiz_id),
                'operation': 'get_quiz_questions'
            })
            raise HTTPException(status_code=500, detail="Failed to fetch questions")