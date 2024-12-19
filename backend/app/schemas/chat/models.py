from typing import List, Literal, Optional
from pydantic import BaseModel

class Message(BaseModel):
    """Base message schema"""
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    messages: List[Message]
    file_id: Optional[str] = None