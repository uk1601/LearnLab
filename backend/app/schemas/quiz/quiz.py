from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class QuizBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class QuizCreate(QuizBase):
    file_id: UUID

class QuizUpdate(QuizBase):
    pass

class QuizInDB(QuizBase):
    id: UUID
    file_id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QuizWithDetails(QuizInDB):
    file_name: str
    total_questions: int
    total_attempts: int
    average_score: Optional[float] = None
    highest_score: Optional[float] = None
    last_attempt: Optional[datetime] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, quiz):
        if not quiz.file:
            raise ValueError("Quiz must have associated file")
        
        # Calculate statistics
        total_attempts = len(quiz.attempts)
        scores = [attempt.score for attempt in quiz.attempts if attempt.score is not None]
        
        return cls(
            id=quiz.id,
            file_id=quiz.file_id,
            user_id=quiz.user_id,
            title=quiz.title,
            description=quiz.description,
            is_active=quiz.is_active,
            created_at=quiz.created_at,
            updated_at=quiz.updated_at,
            file_name=quiz.file.filename,
            total_questions=len(quiz.questions),
            total_attempts=total_attempts,
            average_score=sum(scores) / len(scores) if scores else None,
            highest_score=max(scores) if scores else None,
            last_attempt=max([attempt.end_time for attempt in quiz.attempts if attempt.end_time]) if quiz.attempts else None
        )

class QuizList(BaseModel):
    """Response model for listing quizzes"""
    quizzes: List[QuizWithDetails]
    total: int

    class Config:
        from_attributes = True