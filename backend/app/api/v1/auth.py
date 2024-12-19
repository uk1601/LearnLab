from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from ...core.database import get_db
from ...core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    get_current_user,
    invalidate_refresh_token
)
from ...schemas.user import UserCreate, User, Token
from ...models.user import User as UserModel
from ...models.user_session import UserSession

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user exists
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = UserModel(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(None)
):
    """
    Login user and return access and refresh tokens
    """
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Store refresh token
    refresh_token_expires = datetime.utcnow() + timedelta(days=7)
    db_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=refresh_token_expires,
        device_info=user_agent
    )
    db.add(db_session)
    db.commit()
    

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=User)
async def get_current_user_details(
        current_user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get details of the currently authenticated user
    """
    # Refresh the user data from database to get latest state
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User no longer exists"
        )

    return user
@router.post("/refresh-token", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Get new access token using refresh token
    """
    try:
        # Verify refresh token
        payload = jwt.decode(
            refresh_token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if refresh token exists in database
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or invalid"
            )

        # Create new access token
        access_token = create_access_token(data={"sub": user_id})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
        
@router.get("/me", response_model=User)
async def me(current_user: UserModel = Depends(get_current_user)):
    """
    Get current user
    """
    return current_user

@router.post("/logout")
async def logout(
    current_user: UserModel = Depends(get_current_user),
    refresh_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating refresh tokens
    If refresh_token is provided, only that token is invalidated
    Otherwise, all refresh tokens for the user are invalidated
    """
    if refresh_token:
        # Invalidate specific refresh token
        invalidate_refresh_token(db, refresh_token)
    else:
        # Invalidate all refresh tokens for the user
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id
        ).all()
        for session in sessions:
            db.delete(session)
        db.commit()
    
    return {"message": "Successfully logged out"}