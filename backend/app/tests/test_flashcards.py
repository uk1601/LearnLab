import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.services.flashcard_service import FlashcardService, SpacedRepetitionService
from app.schemas.flashcard import DeckCreate, FlashcardCreate, ReviewRequest
from app.models.flashcard import FlashcardDeck, Flashcard, LearningProgress
from app.utils.flashcard_utils import (
    calculate_review_intervals,
    get_performance_levels,
    calculate_study_schedule,
    analyze_learning_patterns
)

def test_create_deck(db_session):
    user_id = uuid4()
    service = FlashcardService(db_session)
    
    deck_data = DeckCreate(
        title="Test Deck",
        description="Test description"
    )
    
    deck = service.create_deck(user_id, deck_data)
    assert deck.title == "Test Deck"
    assert deck.description == "Test description"
    assert deck.user_id == user_id

def test_create_flashcard(db_session):
    user_id = uuid4()
    service = FlashcardService(db_session)
    
    # Create a deck first
    deck = service.create_deck(
        user_id,
        DeckCreate(title="Test Deck", description="Test description")
    )
    
    card_data = FlashcardCreate(
        front_content="Test front",
        back_content="Test back"
    )
    
    card = service.create_flashcard(deck.id, card_data)
    assert card.front_content == "Test front"
    assert card.back_content == "Test back"
    assert card.deck_id == deck.id

def test_spaced_repetition_algorithm():
    progress = LearningProgress()
    service = SpacedRepetitionService()
    
    # Test good review (quality = 4)
    interval, ease_factor, next_review = service.calculate_next_review(4, progress)
    assert interval > 0
    assert ease_factor > 2.0
    assert next_review > datetime.utcnow()
    
    # Test poor review (quality = 2)
    interval, ease_factor, next_review = service.calculate_next_review(2, progress)
    assert interval == 1
    assert ease_factor < 2.5
    assert next_review > datetime.utcnow()

def test_flashcard_utils():
    # Test review intervals
    intervals = calculate_review_intervals(initial_interval=1, max_interval=30)
    assert len(intervals) > 0
    assert intervals[0] == 1
    assert all(intervals[i] < intervals[i+1] for i in range(len(intervals)-1))
    
    # Test performance levels
    assert get_performance_levels(2.6) == "Excellent"
    assert get_performance_levels(2.2) == "Good"
    assert get_performance_levels(1.8) == "Fair"
    assert get_performance_levels(1.5) == "Needs Review"
    
    # Test study schedule
    schedule = calculate_study_schedule(cards_due=50, available_time=20)
    assert schedule["sessions"] > 0
    assert schedule["cards_per_session"] > 0
    assert schedule["session_duration"] <= 20
    
    # Test learning pattern analysis
    review_history = [
        {"timestamp": datetime.utcnow(), "quality": 4},
        {"timestamp": datetime.utcnow() - timedelta(hours=1), "quality": 5},
        {"timestamp": datetime.utcnow() - timedelta(hours=2), "quality": 3}
    ]
    patterns = analyze_learning_patterns(review_history)
    assert "best_time" in patterns
    assert "average_quality" in patterns
    assert "streak" in patterns
    assert "retention_rate" in patterns

if __name__ == "__main__":
    pytest.main([__file__])
