from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
import uuid
from ...core.database import Base
from datetime import datetime

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey('quizzes.id', ondelete='CASCADE'))
    question_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            question_type.in_(['multiple_choice', 'subjective']),
            name='valid_question_type'
        ),
    )

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    concepts = relationship("QuestionConcept", back_populates="question", cascade="all, delete-orphan")
    multiple_choice_options = relationship("MultipleChoiceOption", back_populates="question", cascade="all, delete-orphan")
    subjective_answer = relationship("SubjectiveAnswer", back_populates="question", cascade="all, delete-orphan", uselist=False)
    responses = relationship("QuestionResponse", back_populates="question", cascade="all, delete-orphan")

    @validates('content', 'explanation')
    def validate_content(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key} cannot be empty")
        return value.strip()

class QuestionConcept(Base):
    __tablename__ = "question_concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE'))
    concept = Column(String(255), nullable=False)

    # Relationships
    question = relationship("Question", back_populates="concepts")

    @validates('concept')
    def validate_concept(self, key, value):
        if not value or not value.strip():
            raise ValueError("Concept cannot be empty")
        return value.strip()

class MultipleChoiceOption(Base):
    __tablename__ = "multiple_choice_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE'))
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("Question", back_populates="multiple_choice_options")

    @validates('content')
    def validate_content(self, key, value):
        if not value or not value.strip():
            raise ValueError("Option content cannot be empty")
        return value.strip()

class SubjectiveAnswer(Base):
    __tablename__ = "subjective_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE'))
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("Question", back_populates="subjective_answer")

    @validates('answer')
    def validate_answer(self, key, value):
        if not value or not value.strip():
            raise ValueError("Answer cannot be empty")
        return value.strip()