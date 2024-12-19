from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/login")

def get_db() -> Generator:
    """
    Database dependency to be used in FastAPI routes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, 
            detail="The user doesn't have enough privileges"
        )
    return current_user


from app.services.podcast_service import (
    AudioService,
    TranscriptService,
    ProgressService,
    AnalyticsService,
    S3Service
)

def get_s3_service() -> S3Service:
    """Get S3 service instance"""
    return S3Service()

def get_audio_service(
    s3_service: S3Service = Depends(get_s3_service)
) -> AudioService:
    """Get audio service instance with S3 dependency"""
    return AudioService(s3_service)

def get_transcript_service(
    s3_service: S3Service = Depends(get_s3_service)
) -> TranscriptService:
    """Get transcript service instance with S3 dependency"""
    return TranscriptService(s3_service)

def get_progress_service() -> ProgressService:
    """Get progress service instance"""
    return ProgressService()

def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance"""
    return AnalyticsService()