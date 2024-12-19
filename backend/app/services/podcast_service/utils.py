from typing import List, Optional
import math
from datetime import datetime, timedelta

def segment_duration(duration: int, segment_length: int = 15) -> List[int]:
    """
    Split duration into segments
    Args:
        duration: Total duration in seconds
        segment_length: Length of each segment in seconds
    Returns:
        List of segment durations
    """
    segments = []
    remaining = duration
    
    while remaining > 0:
        if remaining >= segment_length:
            segments.append(segment_length)
            remaining -= segment_length
        else:
            segments.append(remaining)
            remaining = 0
            
    return segments

def calculate_session_duration(
    start_time: datetime,
    end_time: Optional[datetime] = None,
    max_duration: int = 8 * 60 * 60  # 8 hours
) -> int:
    """
    Calculate session duration with validation
    Args:
        start_time: Session start time
        end_time: Session end time (defaults to now)
        max_duration: Maximum allowed duration in seconds
    Returns:
        Duration in seconds
    """
    if end_time is None:
        end_time = datetime.utcnow()
        
    duration = (end_time - start_time).total_seconds()
    return min(int(duration), max_duration)

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human readable string
    Args:
        seconds: Duration in seconds
    Returns:
        Formatted string (e.g., "1h 30m")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}m")
        
    return " ".join(parts)

def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """
    Estimate reading time for transcript text
    Args:
        text: Transcript text
        wpm: Words per minute reading speed
    Returns:
        Estimated time in seconds
    """
    words = len(text.split())
    minutes = math.ceil(words / wpm)
    return minutes * 60

def is_valid_playback_speed(speed: float) -> bool:
    """
    Validate playback speed
    Args:
        speed: Playback speed multiplier
    Returns:
        True if valid, False otherwise
    """
    ALLOWED_SPEEDS = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    return speed in ALLOWED_SPEEDS