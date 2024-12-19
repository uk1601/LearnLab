from datetime import datetime, timedelta
from typing import Dict
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import func

from app.models.flashcard import FlashcardDeck, Flashcard, LearningProgress
from .base_service import BaseService
from .deck_service import DeckService

class AnalyticsService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.deck_service = DeckService(db)

    def get_user_stats(self, user_id: UUID) -> Dict:
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)

        # Get active decks and cards count
        total_decks = self.db.query(FlashcardDeck)\
            .filter(
                FlashcardDeck.user_id == user_id,
                FlashcardDeck.is_active == True
            ).count()
        
        total_cards = self.db.query(Flashcard)\
            .join(FlashcardDeck)\
            .filter(
                FlashcardDeck.user_id == user_id,
                FlashcardDeck.is_active == True,
                Flashcard.is_active == True
            ).count()

        # Get review statistics
        monthly_reviews = self.db.query(LearningProgress)\
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.last_reviewed >= month_ago
            ).count()

        cards_due = self.db.query(LearningProgress)\
            .join(Flashcard)\
            .join(FlashcardDeck)\
            .filter(
                LearningProgress.user_id == user_id,
                LearningProgress.next_review <= now,
                Flashcard.is_active == True,
                FlashcardDeck.is_active == True
            ).count()

        # Calculate average performance
        avg_performance = self.db.query(func.avg(LearningProgress.ease_factor))\
            .filter(LearningProgress.user_id == user_id)\
            .scalar() or 2.5

        # Count unique files with active decks
        files_with_decks = self.db.query(FlashcardDeck.file_id)\
            .filter(
                FlashcardDeck.user_id == user_id,
                FlashcardDeck.is_active == True
            ).distinct().count()

        return {
            "total_decks": total_decks,
            "total_cards": total_cards,
            "monthly_reviews": monthly_reviews,
            "cards_due": cards_due,
            "average_performance": round(avg_performance, 2),
            "files_with_decks": files_with_decks
        }

    def get_deck_progress(self, user_id: UUID, deck_id: UUID) -> Dict:
        deck = self.deck_service.get_deck(deck_id)
        if not deck or deck.user_id != user_id:
            raise HTTPException(status_code=404, detail="Deck not found")

        total_cards = self.db.query(Flashcard)\
            .filter(
                Flashcard.deck_id == deck_id,
                Flashcard.is_active == True
            ).count()

        mastered_cards = self.db.query(LearningProgress)\
            .join(Flashcard)\
            .filter(
                LearningProgress.user_id == user_id,
                Flashcard.deck_id == deck_id,
                Flashcard.is_active == True,
                LearningProgress.interval >= 21
            ).count()

        learning_cards = self.db.query(LearningProgress)\
            .join(Flashcard)\
            .filter(
                LearningProgress.user_id == user_id,
                Flashcard.deck_id == deck_id,
                Flashcard.is_active == True,
                LearningProgress.interval < 21
            ).count()

        # Get list of pages with cards
        pages_covered = self.db.query(Flashcard.page_number)\
            .filter(
                Flashcard.deck_id == deck_id,
                Flashcard.is_active == True,
                Flashcard.page_number.isnot(None)
            )\
            .distinct()\
            .order_by(Flashcard.page_number)\
            .all()
        
        pages_covered = [page[0] for page in pages_covered if page[0] is not None]

        return {
            "total_cards": total_cards,
            "mastered_cards": mastered_cards,
            "learning_cards": learning_cards,
            "mastery_percentage": round((mastered_cards / total_cards * 100), 2) if total_cards > 0 else 0,
            "pages_covered": pages_covered
        }

    def get_file_learning_status(self, file_id: UUID, user_id: UUID) -> Dict:
        """Get learning status for a specific file"""
        deck = self.db.query(FlashcardDeck)\
            .filter(
                FlashcardDeck.file_id == file_id,
                FlashcardDeck.user_id == user_id,
                FlashcardDeck.is_active == True
            ).first()
        
        if not deck:
            return {
                "has_deck": False,
                "total_cards": 0,
                "mastery_percentage": 0,
                "last_reviewed": None
            }

        total_cards = self.db.query(Flashcard)\
            .filter(
                Flashcard.deck_id == deck.id,
                Flashcard.is_active == True
            ).count()

        mastered_cards = self.db.query(LearningProgress)\
            .join(Flashcard)\
            .filter(
                LearningProgress.user_id == user_id,
                Flashcard.deck_id == deck.id,
                Flashcard.is_active == True,
                LearningProgress.interval >= 21
            ).count()

        last_review = self.db.query(func.max(LearningProgress.last_reviewed))\
            .join(Flashcard)\
            .filter(
                LearningProgress.user_id == user_id,
                Flashcard.deck_id == deck.id
            ).scalar()

        return {
            "has_deck": True,
            "deck_id": deck.id,
            "total_cards": total_cards,
            "mastery_percentage": round((mastered_cards / total_cards * 100), 2) if total_cards > 0 else 0,
            "last_reviewed": last_review
        }