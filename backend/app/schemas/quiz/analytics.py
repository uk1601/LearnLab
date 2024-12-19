from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class FileQuizStats(BaseModel):
    file_id: UUID
    filename: str
    total_quizzes: int
    total_questions: int
    total_attempts: int
    average_score: Optional[float]
    unique_participants: int
    total_time_spent: int  # in seconds
    unique_concepts: int
    multiple_choice_count: int
    subjective_count: int
    success_rate: float

    class Config:
        from_attributes = True

class ConceptProgress(BaseModel):
    concept: str
    success_rate: float
    attempts: int
    last_attempt: Optional[datetime]

class QuestionAnalytics(BaseModel):
    id: UUID
    content: str
    success_rate: float
    average_time: int  # in seconds
    total_attempts: int
    confidence_score: Optional[float]  # For subjective questions

class QuizAnalytics(BaseModel):
    total_attempts: int
    average_score: float
    completion_rate: float
    average_time_per_question: int  # in seconds
    concept_progress: Dict[str, ConceptProgress]
    question_analytics: List[QuestionAnalytics]

class QuizProgressStats(BaseModel):
    attempts_over_time: Dict[str, int]  # date -> number of attempts
    score_progression: Dict[str, float]  # date -> average score
    concept_mastery_trend: Dict[str, Dict[str, float]]  # date -> (concept -> mastery_percentage)
    common_mistakes: List[Dict[str, str]]  # List of question content and common wrong answers

    class Config:
        from_attributes = True