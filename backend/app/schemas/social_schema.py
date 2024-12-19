# app/schemas/social.py

from pydantic import BaseModel, Field
from typing import Optional, List

class MarkdownContent(BaseModel):
    """Schema for markdown content input"""
    content: str = Field(..., description="Markdown content to be posted")
    api_key: str = Field(..., description="API Key for X")
    api_secret_key: str = Field(..., description="API Secret Key for X")
    access_token: str = Field(..., description="Access Token for X")
    access_token_secret: str = Field(..., description="Access Token Secret for X")

class BlogContent(BaseModel):
    """Schema for Blog content input"""
    title: str = Field(..., description="Blog post title")
    body: str = Field(..., description="Blog post body content")

class BloggerResponse(BaseModel):
    """Response schema for Blogger API"""
    message: str
    success: bool
    url: Optional[str] = None

class TwitterResponse(BaseModel):
    """Response schema for Twitter API"""
    message: str
    success: bool
    tweet_ids: Optional[List[str]] = None


class TweetContent(BaseModel):
    tweet: str
