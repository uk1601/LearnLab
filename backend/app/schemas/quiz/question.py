from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator

class QuestionBase(BaseModel):
    question_type: str = Field(..., pattern='^(multiple_choice|subjective)$')
    content: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1)

class MultipleChoiceOptionCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_correct: bool = False

class MultipleChoiceOptionInDB(MultipleChoiceOptionCreate):
    id: UUID
    question_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class SubjectiveAnswerCreate(BaseModel):
    answer: str = Field(..., min_length=1)

class SubjectiveAnswerInDB(SubjectiveAnswerCreate):
    id: UUID
    question_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionConceptCreate(BaseModel):
    concept: str = Field(..., min_length=1, max_length=255)

class QuestionConceptInDB(QuestionConceptCreate):
    id: UUID
    question_id: UUID

    class Config:
        from_attributes = True

class QuestionCreate(QuestionBase):
    concepts: List[str] = Field(..., min_items=1)
    options: Optional[List[MultipleChoiceOptionCreate]] = None
    answer: Optional[SubjectiveAnswerCreate] = None

    @validator('options')
    def validate_options(cls, v, values):
        if values.get('question_type') == 'multiple_choice':
            if not v or len(v) < 2:
                raise ValueError('Multiple choice questions must have at least 2 options')
            if sum(1 for opt in v if opt.is_correct) != 1:
                raise ValueError('Multiple choice questions must have exactly one correct answer')
        elif v is not None:
            raise ValueError('Subjective questions should not have options')
        return v

    @validator('answer')
    def validate_answer(cls, v, values):
        if values.get('question_type') == 'subjective':
            if not v:
                raise ValueError('Subjective questions must have an answer')
        elif v is not None:
            raise ValueError('Multiple choice questions should not have a subjective answer')
        return v

class QuestionUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    explanation: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None

class QuestionInDB(QuestionBase):
    id: UUID
    quiz_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QuestionWithOptions(QuestionInDB):
    options: List[MultipleChoiceOptionInDB] = Field(alias='multiple_choice_options')
    concepts: List[QuestionConceptInDB]

    class Config:
        from_attributes = True

class QuestionWithAnswer(QuestionInDB):
    answer: SubjectiveAnswerInDB = Field(alias='subjective_answer')
    concepts: List[QuestionConceptInDB]

    class Config:
        from_attributes = True