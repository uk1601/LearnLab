"""
Version 1 of the LearnLab API
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .files import router as files_router
from .flashcards import router as flashcards_router
from .quiz import router as quiz_router
from .podcast import podcast_router, progress_router, analytics_router
from .generate import router as generate_router
from .chat import router as chat_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(flashcards_router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(quiz_router, prefix="/quiz", tags=["quizzes"])
api_router.include_router(podcast_router, prefix="/podcasts", tags=["podcasts"])
api_router.include_router(progress_router, prefix="/podcasts", tags=["podcasts"])
api_router.include_router(analytics_router, prefix="/podcasts", tags=["podcasts"])
api_router.include_router(generate_router, prefix="/generate", tags=["generation"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

__all__ = ["api_router"]