from datetime import datetime, timedelta
from typing import List, Dict
import math

def calculate_review_intervals(initial_interval: int = 1, max_interval: int = 365) -> List[int]:
    """
    Calculate the sequence of review intervals based on the SM-2 algorithm
    """
    intervals = [initial_interval]
    current_interval = initial_interval
    
    while current_interval < max_interval:
        next_interval = math.ceil(current_interval * 2.5)
        if next_interval > max_interval:
            break
        intervals.append(next_interval)
        current_interval = next_interval
    
    return intervals

def get_performance_level(ease_factor: float) -> str:
    """
    Convert ease factor to performance level
    """
    if ease_factor >= 2.5:
        return "Excellent"
    elif ease_factor >= 2.1:
        return "Good"
    elif ease_factor >= 1.7:
        return "Fair"
    else:
        return "Needs Review"

def calculate_study_schedule(cards_due: int, available_time: int = 30) -> Dict:
    """
    Calculate optimal study schedule given number of due cards and available time
    
    Args:
        cards_due: Number of cards due for review
        available_time: Available time in minutes
    
    Returns:
        Dict containing recommended cards per session and session duration
    """
    AVG_CARD_TIME = 0.5  # Average time per card in minutes
    
    total_time_needed = cards_due * AVG_CARD_TIME
    if total_time_needed <= available_time:
        return {
            "sessions": 1,
            "cards_per_session": cards_due,
            "session_duration": math.ceil(total_time_needed)
        }
    
    optimal_sessions = math.ceil(total_time_needed / available_time)
    cards_per_session = math.ceil(cards_due / optimal_sessions)
    
    return {
        "sessions": optimal_sessions,
        "cards_per_session": cards_per_session,
        "session_duration": math.ceil(cards_per_session * AVG_CARD_TIME)
    }

def analyze_learning_patterns(review_history: List[Dict]) -> Dict:
    """
    Analyze learning patterns from review history
    """
    if not review_history:
        return {
            "best_time": None,
            "average_quality": 0,
            "streak": 0,
            "retention_rate": 0
        }
    
    # Group reviews by hour
    hour_performance = {}
    for review in review_history:
        hour = review['timestamp'].hour
        if hour not in hour_performance:
            hour_performance[hour] = []
        hour_performance[hour].append(review['quality'])
    
    # Find best performing hour
    best_hour = max(hour_performance.items(), 
                   key=lambda x: sum(x[1])/len(x[1]))[0]
    
    # Calculate average quality
    all_qualities = [r['quality'] for r in review_history]
    avg_quality = sum(all_qualities) / len(all_qualities)
    
    # Calculate current streak
    streak = 0
    for review in reversed(review_history):
        if review['quality'] >= 4:
            streak += 1
        else:
            break
    
    # Calculate retention rate (percentage of reviews with quality >= 3)
    retention = len([q for q in all_qualities if q >= 3]) / len(all_qualities)
    
    return {
        "best_time": f"{best_hour:02d}:00",
        "average_quality": round(avg_quality, 2),
        "streak": streak,
        "retention_rate": round(retention * 100, 2)
    }

def get_file_statistics(cards: List[Dict], page_count: int) -> Dict:
    """
    Calculate statistics for file-based learning
    
    Args:
        cards: List of flashcards with page numbers
        page_count: Total number of pages in the file
    
    Returns:
        Dict containing file coverage statistics
    """
    if not cards:
        return {
            "total_pages": page_count,
            "pages_with_cards": 0,
            "cards_per_page": 0,
            "coverage_percentage": 0,
            "page_distribution": {}
        }
    
    # Get pages with cards
    pages_with_cards = set(card['page_number'] for card in cards if card.get('page_number'))
    
    # Calculate page distribution
    page_distribution = {}
    for card in cards:
        page = card.get('page_number')
        if page:
            page_distribution[page] = page_distribution.get(page, 0) + 1
    
    return {
        "total_pages": page_count,
        "pages_with_cards": len(pages_with_cards),
        "cards_per_page": round(len(cards) / len(pages_with_cards), 2) if pages_with_cards else 0,
        "coverage_percentage": round(len(pages_with_cards) / page_count * 100, 2) if page_count > 0 else 0,
        "page_distribution": page_distribution
    }

def generate_study_insights(stats: Dict) -> List[str]:
    """
    Generate insights based on learning statistics
    
    Args:
        stats: Dictionary containing learning statistics
    
    Returns:
        List of insight messages
    """
    insights = []
    
    # Coverage insights
    if stats['coverage_percentage'] < 30:
        insights.append("Consider creating cards for more pages to improve coverage")
    elif stats['coverage_percentage'] > 80:
        insights.append("Excellent file coverage! Focus on reviewing existing cards")
    
    # Cards per page insights
    if stats['cards_per_page'] < 2:
        insights.append("Try adding more cards per page for comprehensive learning")
    elif stats['cards_per_page'] > 5:
        insights.append("You have many cards per page. Ensure they cover distinct concepts")
    
    # Distribution insights
    page_distribution = stats['page_distribution']
    if page_distribution:
        max_cards = max(page_distribution.values())
        min_cards = min(page_distribution.values())
        if max_cards > min_cards * 3:
            insights.append("Card distribution is uneven across pages. Consider balancing")
    
    return insights

def recommend_review_strategy(learning_progress: Dict) -> Dict:
    """
    Recommend review strategy based on learning progress
    
    Args:
        learning_progress: Dictionary containing learning progress statistics
    
    Returns:
        Dict containing review recommendations
    """
    cards_due = learning_progress.get('cards_due', 0)
    mastery_percentage = learning_progress.get('mastery_percentage', 0)
    retention_rate = learning_progress.get('retention_rate', 0)
    
    strategy = {
        "priority": "medium",
        "session_count": 1,
        "cards_per_session": cards_due,
        "recommendations": []
    }
    
    if cards_due > 20:
        strategy["priority"] = "high"
        strategy["session_count"] = math.ceil(cards_due / 20)
        strategy["cards_per_session"] = 20
        strategy["recommendations"].append("Break reviews into multiple sessions")
    
    if mastery_percentage < 50:
        strategy["priority"] = "high"
        strategy["recommendations"].append("Focus on improving card mastery")
    
    if retention_rate < 70:
        strategy["recommendations"].append("Consider reviewing cards more frequently")
    
    if not strategy["recommendations"]:
        strategy["recommendations"].append("Maintain current study pattern")
    
    return strategy
