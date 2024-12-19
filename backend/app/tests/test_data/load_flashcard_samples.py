from datetime import datetime, timedelta
import random
from uuid import UUID

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.flashcard import FlashcardDeck, Flashcard, LearningProgress
from app.services.flashcard_service import FlashcardService

# Sample data based on machine learning concepts
SAMPLE_DECKS = [
    {
        "file_id": "70160a20-bec3-4128-a7f0-132efbf294fa",
        "title": "Machine Learning Fundamentals",
        "description": "Basic concepts and terminologies in machine learning"
    },
    {
        "file_id": "32db86f1-3420-4f0d-aaa0-966673819605",
        "title": "Neural Networks",
        "description": "Deep learning and neural network concepts"
    },
    {
        "file_id": "f7ecee5f-c227-4102-b5ea-ae44469a5ed2",
        "title": "Model Evaluation",
        "description": "Techniques for evaluating machine learning models"
    }
]

SAMPLE_CARDS = {
    "Machine Learning Fundamentals": [
        {
            "front_content": "What is supervised learning?",
            "back_content": "A type of machine learning where the model is trained on labeled data to predict outputs for unseen inputs.",
            "page_number": 1
        },
        {
            "front_content": "What is the difference between classification and regression?",
            "back_content": "Classification predicts discrete class labels, while regression predicts continuous values.",
            "page_number": 2
        },
        {
            "front_content": "Explain overfitting",
            "back_content": "When a model learns the training data too well, including noise, leading to poor generalization.",
            "page_number": 3
        }
    ],
    "Neural Networks": [
        {
            "front_content": "What is a neural network?",
            "back_content": "A computational model inspired by biological neural networks, consisting of connected nodes organized in layers.",
            "page_number": 1
        },
        {
            "front_content": "What is backpropagation?",
            "back_content": "An algorithm for training neural networks by calculating gradients of the loss function with respect to weights.",
            "page_number": 2
        },
        {
            "front_content": "What is an activation function?",
            "back_content": "A function that determines the output of a neural network node, introducing non-linearity into the model.",
            "page_number": 3
        }
    ],
    "Model Evaluation": [
        {
            "front_content": "What is cross-validation?",
            "back_content": "A technique to assess model performance by partitioning data into training and testing sets multiple times.",
            "page_number": 1
        },
        {
            "front_content": "What is precision and recall?",
            "back_content": "Precision measures the accuracy of positive predictions, while recall measures the fraction of positives identified.",
            "page_number": 2
        },
        {
            "front_content": "What is the ROC curve?",
            "back_content": "A graphical plot showing the diagnostic ability of a binary classifier at various discrimination thresholds.",
            "page_number": 3
        }
    ]
}

def load_sample_data(user_id: UUID):
    """Load sample flashcard data for a user"""
    db = SessionLocal()
    service = FlashcardService(db)
    
    try:
        print(f"\nLoading sample data for user {user_id}")
        
        # Create decks
        decks = {}
        for deck_data in SAMPLE_DECKS:
            print(f"\nCreating deck: {deck_data['title']}")
            deck = service.create_deck(user_id, deck_data)
            decks[deck.title] = deck
            print(f"Created deck with ID: {deck.id}")
        
        # Create cards for each deck
        total_cards = 0
        for deck_title, cards in SAMPLE_CARDS.items():
            deck = decks[deck_title]
            print(f"\nAdding cards to deck: {deck_title}")
            
            for card_data in cards:
                card = service.create_flashcard(deck.id, card_data)
                total_cards += 1
                
                # Simulate learning progress with random review history
                for _ in range(random.randint(1, 5)):
                    quality = random.randint(3, 5)
                    service.record_review(user_id, card.id, quality)
        
        print("\nSample data loading completed!")
        print(f"Created {len(decks)} decks with {total_cards} total cards")
        
        # Print some statistics
        stats = service.get_user_stats(user_id)
        print("\nUser Statistics:")
        print(f"Total Decks: {stats['total_decks']}")
        print(f"Total Cards: {stats['total_cards']}")
        print(f"Monthly Reviews: {stats['monthly_reviews']}")
        print(f"Cards Due: {stats['cards_due']}")
        print(f"Average Performance: {stats['average_performance']}")
        print(f"Files with Decks: {stats['files_with_decks']}")

    except Exception as e:
        print(f"Error loading sample data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":    
    USER_ID = "340003bc-3dbc-4c0b-8c4c-777126934e5d"  # Admin user ID
    load_sample_data(UUID(USER_ID))
