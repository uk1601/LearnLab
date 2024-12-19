from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import Column, ForeignKey, String, Text, Float, Integer, DateTime, Boolean, func
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.database import Base

class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"
    
    id = Column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PSQL_UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'))
    file_id = Column(PSQL_UUID(as_uuid=True), ForeignKey("files.id", ondelete='CASCADE'))
    title = Column(String(255), nullable=False)  # Match VARCHAR(255) from SQL
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="decks")
    file = relationship("File", back_populates="deck")
    cards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 255:
            raise ValueError("Title cannot be longer than 255 characters")
        return title

    @hybrid_property
    def active_cards_count(self) -> int:
        """Get count of active cards in deck"""
        return sum(1 for card in self.cards if card.is_active)

    @hybrid_property
    def mastery_percentage(self) -> float:
        """Calculate mastery percentage of deck"""
        active_cards = [card for card in self.cards if card.is_active]
        if not active_cards:
            return 0.0
        
        mastered = sum(1 for card in active_cards if card.is_mastered)
        return (mastered / len(active_cards)) * 100

    def get_due_cards(self, user_id: PSQL_UUID) -> List["Flashcard"]:
        """Get all due cards for a user"""
        return [card for card in self.cards 
                if card.is_active and card.is_due(user_id)]

class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    deck_id = Column(PSQL_UUID(as_uuid=True), ForeignKey("flashcard_decks.id", ondelete='CASCADE'))
    front_content = Column(Text, nullable=False)
    back_content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deck = relationship("FlashcardDeck", back_populates="cards")
    learning_progress = relationship("LearningProgress", back_populates="flashcard", cascade="all, delete-orphan")

    @validates('front_content', 'back_content')
    def validate_content(self, key, content):
        if not content or not content.strip():
            raise ValueError(f"{key} cannot be empty")
        return content.strip()

    @hybrid_property
    def is_mastered(self) -> bool:
        """Check if card is mastered (interval >= 21 days)"""
        if not self.learning_progress:
            return False
        return any(progress.interval >= 21 for progress in self.learning_progress)

    def is_due(self, user_id: PSQL_UUID) -> bool:
        """Check if card is due for review for a specific user"""
        progress = next((p for p in self.learning_progress if p.user_id == user_id), None)
        if not progress:
            return True
        return progress.next_review <= datetime.utcnow()

    def get_progress(self, user_id: PSQL_UUID) -> Optional["LearningProgress"]:
        """Get learning progress for a specific user"""
        return next((p for p in self.learning_progress if p.user_id == user_id), None)

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PSQL_UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'))
    flashcard_id = Column(PSQL_UUID(as_uuid=True), ForeignKey("flashcards.id", ondelete='CASCADE'))
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    last_reviewed = Column(DateTime(timezone=True))
    next_review = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_progress")
    flashcard = relationship("Flashcard", back_populates="learning_progress")

    @validates('ease_factor')
    def validate_ease_factor(self, key, value):
        if value < 1.3:  # Minimum ease factor in SM-2
            return 1.3
        return value

    @hybrid_property
    def is_due(self) -> bool:
        """Check if review is due"""
        if not self.next_review:
            return True
        return self.next_review <= datetime.utcnow()

    @hybrid_property
    def days_until_review(self) -> Optional[int]:
        """Get days until next review"""
        if not self.next_review:
            return None
        delta = self.next_review - datetime.utcnow()
        return max(0, delta.days)

    @hybrid_property
    def performance_level(self) -> str:
        """Get performance level based on ease factor"""
        if self.ease_factor >= 2.5:
            return "Excellent"
        elif self.ease_factor >= 2.1:
            return "Good"
        elif self.ease_factor >= 1.7:
            return "Fair"
        else:
            return "Needs Review"