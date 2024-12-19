from fastapi import APIRouter
from .quiz import router as quiz_router
from .question import router as question_router
from .attempt import router as attempt_router
from .analytics import router as analytics_router

router = APIRouter()

router.include_router(quiz_router, prefix="", tags=["quizzes"])
router.include_router(question_router, prefix="/questions", tags=["quiz questions"])
router.include_router(attempt_router, prefix="/attempts", tags=["quiz attempts"])
router.include_router(analytics_router, prefix="/analytics", tags=["quiz analytics"])

__all__ = ["router"]