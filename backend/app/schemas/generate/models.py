from uuid import UUID
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    """Request schema for generation endpoint"""
    query: str
    file_id: UUID
    podcast: bool = False
    quiz: bool = False
    flashcards: bool = False

class GenerateResponse(BaseModel):
    """Response schema for generation endpoint"""
    is_podcast_generating: bool = False
    is_quiz_generating: bool = False
    is_flashcards_generating: bool = False