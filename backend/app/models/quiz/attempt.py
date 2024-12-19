from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Float, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ...core.database import Base
from datetime import datetime

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey('quizzes.id', ondelete='CASCADE'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    score = Column(Float)
    status = Column(String(50), default='in_progress')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            status.in_(['in_progress', 'completed']),
            name='valid_attempt_status'
        ),
    )

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")
    responses = relationship("QuestionResponse", back_populates="attempt", cascade="all, delete-orphan")

class QuestionResponse(Base):
    __tablename__ = "question_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey('quiz_attempts.id', ondelete='CASCADE'))
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE'))
    response = Column(Text, nullable=False)
    is_correct = Column(Boolean)
    confidence_score = Column(Float)
    time_taken = Column(Integer)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("Question", back_populates="responses")