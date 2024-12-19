from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.flashcard import FlashcardDeck, Flashcard, LearningProgress
from app.models.file import File
from app.schemas.flashcard import (
    DeckCreate, FlashcardCreate, DeckUpdate, FlashcardUpdate,
    DeckWithFile
)

from .deck_service import DeckService
from .card_service import CardService
from .review_service import ReviewService
from .analytics_service import AnalyticsService

class FlashcardService:
    """Main service that delegates to specialized services"""
    
    def __init__(self, db: Session):
        self.db = db
        self.deck_service = DeckService(db)
        self.card_service = CardService(db)
        self.review_service = ReviewService(db)
        self.analytics_service = AnalyticsService(db)

    # Deck-related methods
    def get_deck(self, deck_id: UUID) -> Optional[FlashcardDeck]:
        return self.deck_service.get_deck(deck_id)

    def get_user_decks(self, user_id: UUID) -> List[DeckWithFile]:
        return self.deck_service.get_user_decks(user_id)
    
    def get_user_file_decks(self, user_id: UUID, file_id: UUID) -> List[DeckWithFile]:
        return self.deck_service.get_user_decks(user_id, file_id)

    def create_deck(self, user_id: UUID, deck_data: DeckCreate) -> FlashcardDeck:
        return self.deck_service.create_deck(user_id, deck_data)

    def update_deck(self, deck_id: UUID, deck_data: DeckUpdate) -> Optional[FlashcardDeck]:
        return self.deck_service.update_deck(deck_id, deck_data)

    def delete_deck(self, deck_id: UUID) -> bool:
        return self.deck_service.delete_deck(deck_id)

    # Card-related methods
    def get_flashcard(self, card_id: UUID) -> Optional[Flashcard]:
        return self.card_service.get_flashcard(card_id)

    def create_flashcard(self, deck_id: UUID, card_data: FlashcardCreate) -> Flashcard:
        return self.card_service.create_flashcard(deck_id, card_data)

    def update_flashcard(self, card_id: UUID, card_data: FlashcardUpdate) -> Optional[Flashcard]:
        return self.card_service.update_flashcard(card_id, card_data)

    def delete_flashcard(self, card_id: UUID) -> bool:
        return self.card_service.delete_flashcard(card_id)

    def get_cards_by_page(self, deck_id: UUID) -> List[Flashcard]:
        return self.card_service.get_cards_by_page(deck_id)

    # Review-related methods
    def get_due_cards(self, user_id: UUID, deck_id: Optional[UUID] = None) -> List[Flashcard]:
        return self.review_service.get_due_cards(user_id, deck_id)

    def record_review(self, user_id: UUID, card_id: UUID, quality: int) -> LearningProgress:
        return self.review_service.record_review(user_id, card_id, quality)

    # Analytics-related methods
    def get_user_stats(self, user_id: UUID) -> Dict:
        return self.analytics_service.get_user_stats(user_id)

    def get_deck_progress(self, user_id: UUID, deck_id: UUID) -> Dict:
        return self.analytics_service.get_deck_progress(user_id, deck_id)

    def get_file_learning_status(self, file_id: UUID, user_id: UUID) -> Dict:
        return self.analytics_service.get_file_learning_status(file_id, user_id)