from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException

from app.models.flashcard import Flashcard
from app.schemas.flashcard import FlashcardCreate, FlashcardUpdate
from .base_service import BaseService
from .deck_service import DeckService

class CardService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.deck_service = DeckService(db)

    def get_flashcard(self, card_id: UUID) -> Optional[Flashcard]:
        return self.db.query(Flashcard).filter(
            Flashcard.id == card_id,
            Flashcard.is_active == True
        ).first()

    def create_flashcard(self, deck_id: UUID, card_data: FlashcardCreate) -> Flashcard:
        # Verify deck exists and is active
        deck = self.deck_service.get_deck(deck_id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        card = Flashcard(
            deck_id=deck_id,
            front_content=card_data.front_content,
            back_content=card_data.back_content,
            page_number=card_data.page_number
        )
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        return card

    def update_flashcard(self, card_id: UUID, card_data: FlashcardUpdate) -> Optional[Flashcard]:
        card = self.get_flashcard(card_id)
        if card:
            for key, value in card_data.dict(exclude_unset=True).items():
                setattr(card, key, value)
            self.db.commit()
            self.db.refresh(card)
        return card

    def delete_flashcard(self, card_id: UUID) -> bool:
        card = self.get_flashcard(card_id)
        if card:
            # Soft delete
            card.is_active = False
            self.db.commit()
            return True
        return False

    def get_cards_by_page(self, deck_id: UUID) -> List[Flashcard]:
        return self.db.query(Flashcard).filter(
            Flashcard.deck_id == deck_id,            
            Flashcard.is_active == True
        ).all()