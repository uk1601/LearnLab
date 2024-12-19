from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.flashcard import Flashcard, LearningProgress, FlashcardDeck
from .base_service import BaseService
from .card_service import CardService

class ReviewService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.card_service = CardService(db)

    def calculate_next_review(self, quality: int, learning_progress: LearningProgress) -> Tuple[int, float, datetime]:
        """
        Implements SuperMemo SM-2 algorithm
        Args:
            quality: Review quality (0-5)
            learning_progress: LearningProgress object
            
        Returns:
            Tuple[int, float, datetime]: (interval, ease_factor, next_review)
        
        Raises:
            ValueError: If quality is not between 0 and 5
        """
        # Validate input quality
        if not isinstance(quality, int) or quality < 0 or quality > 5:
            raise ValueError("Quality must be an integer between 0 and 5")

        # Initialize default values if None
        if learning_progress.repetitions is None:
            learning_progress.repetitions = 0
        if learning_progress.interval is None:
            learning_progress.interval = 1
        if learning_progress.ease_factor is None:
            learning_progress.ease_factor = 2.5

        try:
            # Calculate new values based on quality
            if quality < 3:
                learning_progress.repetitions = 0
                learning_progress.interval = 1
            else:
                if learning_progress.repetitions == 0:
                    learning_progress.interval = 1
                elif learning_progress.repetitions == 1:
                    learning_progress.interval = 6
                else:
                    # Ensure both values are not None before multiplication
                    interval = learning_progress.interval or 1
                    ease_factor = learning_progress.ease_factor or 2.5
                    learning_progress.interval = round(interval * ease_factor)

                learning_progress.repetitions += 1

            # Update ease factor
            ease_factor_change = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            learning_progress.ease_factor = max(1.3, learning_progress.ease_factor + ease_factor_change)

            # Calculate next review date
            next_review = datetime.utcnow() + timedelta(days=max(1, learning_progress.interval))

            return learning_progress.interval, learning_progress.ease_factor, next_review

        except Exception as e:
            # Log the error with current values
            print(f"Error in calculate_next_review: {str(e)}")
            print(f"Current values - interval: {learning_progress.interval}, "
                  f"ease_factor: {learning_progress.ease_factor}, "
                  f"repetitions: {learning_progress.repetitions}")
            # Return safe default values
            learning_progress.interval = 1
            learning_progress.ease_factor = 2.5
            return 1, 2.5, datetime.utcnow() + timedelta(days=1)

    def get_due_cards(self, user_id: UUID, deck_id: Optional[UUID] = None) -> List[Flashcard]:
        """
        Get all due cards for a user, optionally filtered by deck
        """
        try:
            # Base query with all necessary joins
            query = self.db.query(Flashcard)\
                .join(LearningProgress)\
                .join(FlashcardDeck)\
                .filter(
                    LearningProgress.user_id == user_id,
                    LearningProgress.next_review <= datetime.utcnow(),
                    Flashcard.is_active == True,
                    FlashcardDeck.is_active == True
                )
            
            # Add deck filter if provided
            if deck_id:
                query = query.filter(FlashcardDeck.id == deck_id)
            
            return query.all()
            
        except SQLAlchemyError as e:
            print(f"Database error in get_due_cards: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve due cards"
            )

    def record_review(self, user_id: UUID, card_id: UUID, quality: int) -> LearningProgress:
        """
        Record a review for a flashcard
        Args:
            user_id: ID of the user
            card_id: ID of the flashcard
            quality: Review quality (0-5)
            
        Returns:
            LearningProgress: Updated progress object
            
        Raises:
            HTTPException: If card not found or on database error
        """
        try:
            # Validate card exists
            card = self.card_service.get_flashcard(card_id)
            if not card:
                raise HTTPException(status_code=404, detail="Card not found")

            # Get or create progress
            progress = self.db.query(LearningProgress)\
                .filter_by(user_id=user_id, flashcard_id=card_id)\
                .first()
            
            if not progress:
                progress = LearningProgress(
                    user_id=user_id,
                    flashcard_id=card_id,
                    interval=1,
                    ease_factor=2.5,
                    repetitions=0
                )
                self.db.add(progress)

            # Calculate new values
            try:
                interval, ease_factor, next_review = self.calculate_next_review(quality, progress)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

            # Update progress
            progress.interval = interval
            progress.ease_factor = ease_factor
            progress.last_reviewed = datetime.utcnow()
            progress.next_review = next_review
            
            self.db.commit()
            self.db.refresh(progress)
            return progress
            
        except SQLAlchemyError as e:
            print(f"Database error in record_review: {str(e)}")
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to record review"
            )