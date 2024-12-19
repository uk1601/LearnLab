from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict

from ...core.deps import get_db, get_current_user
from ...models.user import User
from ...services.s3 import S3Service
from ...services.sample_data_service import SampleDataService

router = APIRouter()

@router.post("/populate-sample-data", response_model=Dict)
async def populate_sample_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Populate sample learning content for the current user.
    Creates files, flashcards, quizzes, and podcasts with sample data.
    """
    s3_service = S3Service()
    sample_data_service = SampleDataService(db, s3_service)
    
    return await sample_data_service.populate_user_data(current_user.id)
