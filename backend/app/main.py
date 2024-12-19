from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import auth, files, flashcards, podcast, quiz, websocket, sample_data, generate, chat, social
from .core.config import settings
from .core.database import engine, Base

from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import json

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LearnLab API",
    description="Backend API for LearnLab application",
    version="1.0.0"
)

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with specific origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     allow_control_headers=["*"],
#     expose_headers=["*"]
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.middleware("http")
async def custom_cors_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Include routers
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    files.router,
    prefix="/api/files",
    tags=["Files"]
)

app.include_router(
    flashcards.router,
    prefix="/api/flashcards",
    tags=["Flashcards"]
)

app.include_router(
    podcast.podcast_router,
    prefix="/api/podcasts",
    tags=["Podcasts"]
)

app.include_router(
    podcast.progress_router,
    prefix="/api/podcasts",
    tags=["Podcast Progress"]
)

app.include_router(
    podcast.analytics_router,
    prefix="/api/podcasts",
    tags=["Podcast Analytics"]
)

app.include_router(
    quiz.router,
    prefix="/api/quiz",
    tags=["Quizzes"]
)

app.include_router(
    websocket.router,
    tags=["WebSocket"]
)

app.include_router(
    chat.router,
    prefix="/api/chat",
    tags=["Chat"]
)
app.include_router(
    generate.router,
    prefix="/api/generate",
    tags=["Generation"]
)
app.include_router(
    sample_data.router,
    prefix="/api/sample-data",
    tags=["Sample Data"]
)

app.include_router(
    social.router,
    prefix="/api/social",
    tags=["Social Media"]
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to LearnLab API",
        "documentation": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Service is running"
    }    
