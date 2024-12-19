from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, validator

class AttemptBase(BaseModel):
    quiz_id: UUID

class AttemptCreate(AttemptBase):
    pass

class AttemptUpdate(BaseModel):
    end_time: Optional[datetime] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, pattern='^(in_progress|completed)$')

class AttemptInDB(AttemptBase):
    id: UUID
    user_id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    score: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResponseCreate(BaseModel):
    question_id: UUID
    response: str = Field(..., min_length=1)
    time_taken: int = Field(..., ge=0)  # in seconds

class ResponseUpdate(BaseModel):
    is_correct: bool
    confidence_score: Optional[float] = Field(None, ge=0, le=1)

class ResponseInDB(ResponseCreate):
    id: UUID
    attempt_id: UUID
    is_correct: Optional[bool]
    confidence_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionStats(BaseModel):
    question_id: UUID
    content: str
    correct_responses: int
    total_attempts: int
    average_time: float
    success_rate: float

class QuizAttemptStats(BaseModel):
    total_attempts: int
    average_score: float
    average_completion_time: int  # in seconds
    question_stats: List[QuestionStats]
    concept_mastery: Dict[str, float]  # concept -> mastery percentage

    class Config:
        from_attributes = True