from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

# Base File Schemas
class FileBase(BaseModel):
    filename: str
    mime_type: str
    s3_key: str

class FileInfo(FileBase):
    file_size: Optional[int] = None
    is_deleted: bool = False

    class Config:
        orm_mode = True

# Base Deck Schemas
class DeckBase(BaseModel):
    title: str
    description: Optional[str] = None

class DeckCreate(DeckBase):
    file_id: UUID

class DeckUpdate(DeckBase):
    pass

class DeckInDB(DeckBase):
    id: UUID
    user_id: UUID
    file_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DeckWithFile(DeckBase):
    id: UUID
    user_id: UUID
    file_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    file_name: str
    file_type: str
    file_url: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, deck):
        # Custom from_orm to handle file fields
        if not deck.file:
            raise ValueError("Deck must have associated file")
        
        return cls(
            id=deck.id,
            user_id=deck.user_id,
            file_id=deck.file_id,
            title=deck.title,
            description=deck.description,
            is_active=deck.is_active,
            created_at=deck.created_at,
            updated_at=deck.updated_at,
            file_name=deck.file.filename,
            file_type=deck.file.mime_type,
            file_url=deck.file.s3_key
        )

# Flashcard Schemas
class FlashcardBase(BaseModel):
    front_content: str
    back_content: str
    page_number: Optional[int] = None

class FlashcardCreate(FlashcardBase):
    pass

class FlashcardUpdate(FlashcardBase):
    pass

class FlashcardInDB(FlashcardBase):
    id: UUID
    deck_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Learning Progress Schemas
class ReviewRequest(BaseModel):
    quality: int = Field(..., ge=0, le=5, description="Rating of recall quality (0-5)")

class ReviewResponse(BaseModel):
    id: UUID
    user_id: UUID
    flashcard_id: UUID
    ease_factor: float
    interval: int
    repetitions: int
    last_reviewed: datetime
    next_review: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Analytics Schemas
class DeckProgress(BaseModel):
    total_cards: int
    mastered_cards: int
    learning_cards: int
    mastery_percentage: float
    pages_covered: Optional[List[int]] = []

    class Config:
        orm_mode = True

class UserStats(BaseModel):
    total_decks: int
    total_cards: int
    monthly_reviews: int
    cards_due: int
    average_performance: float
    files_with_decks: int

    class Config:
        orm_mode = True

# File Learning Status
class FileLearningStatus(BaseModel):
    has_deck: bool
    deck_id: Optional[UUID] = None
    total_cards: int
    mastery_percentage: float
    last_reviewed: Optional[datetime] = None

    class Config:
        orm_mode = True

# Response Models for API
class DeckList(BaseModel):
    """Response model for listing decks"""
    decks: List[DeckWithFile]
    total: int

    class Config:
        orm_mode = True

class FlashcardList(BaseModel):
    """Response model for listing flashcards"""
    cards: List[FlashcardInDB]
    total: int

    class Config:
        orm_mode = True

class DueCards(BaseModel):
    """Response model for due cards"""
    cards: List[FlashcardInDB]
    total_due: int
    next_review_in: Optional[int] = None  # minutes until next card is due

    class Config:
        orm_mode = True