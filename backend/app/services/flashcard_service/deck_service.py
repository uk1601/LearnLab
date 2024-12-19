from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import joinedload
from fastapi import HTTPException

from app.models.flashcard import FlashcardDeck
from app.models.file import File
from app.schemas.flashcard import DeckCreate, DeckUpdate, DeckWithFile
from .base_service import BaseService

class DeckService(BaseService):
    def verify_file_access(self, user_id: UUID, file_id: UUID) -> File:
        """Verify user has access to the file"""
        file = self.db.query(File).filter(File.id == file_id).first()
        if not file or file.user_id != user_id:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        return file

    def get_deck(self, deck_id: UUID) -> Optional[FlashcardDeck]:
        """Get a single deck with file information loaded"""
        return self.db.query(FlashcardDeck).options(
            joinedload(FlashcardDeck.file)
        ).filter(
            FlashcardDeck.id == deck_id,
            FlashcardDeck.is_active == True
        ).first()

    def get_user_decks(self, user_id: UUID, file_id: UUID = None) -> List[DeckWithFile]:
        """Get all decks for a user with file information"""
        decks = self.db.query(FlashcardDeck).options(
            joinedload(FlashcardDeck.file)
        ).filter(
            FlashcardDeck.user_id == user_id,
            FlashcardDeck.is_active == True,
            FlashcardDeck.file_id == file_id if file_id else True
        ).all()
        
        return [DeckWithFile.from_orm(deck) for deck in decks]

    def create_deck(self, user_id: UUID, deck_data: DeckCreate) -> FlashcardDeck:
        # Verify file access
        self.verify_file_access(user_id, deck_data.file_id)
        
        # # Check if deck already exists for this file
        # existing_deck = self.db.query(FlashcardDeck).filter(
        #     FlashcardDeck.file_id == deck_data.file_id,
        #     FlashcardDeck.is_active == True
        # ).first()
        
        # if existing_deck:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="A deck already exists for this file"
        #     )

        deck = FlashcardDeck(
            user_id=user_id,
            file_id=deck_data.file_id,
            title=deck_data.title,
            description=deck_data.description
        )
        self.db.add(deck)
        self.db.commit()
        self.db.refresh(deck)
        return deck

    def update_deck(self, deck_id: UUID, deck_data: DeckUpdate) -> Optional[FlashcardDeck]:
        deck = self.get_deck(deck_id)
        if deck:
            for key, value in deck_data.dict(exclude_unset=True).items():
                setattr(deck, key, value)
            self.db.commit()
            self.db.refresh(deck)
        return deck

    def delete_deck(self, deck_id: UUID) -> bool:
        deck = self.get_deck(deck_id)
        if deck:
            # Soft delete
            deck.is_active = False
            self.db.commit()
            return True
        return False