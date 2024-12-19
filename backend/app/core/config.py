from typing import Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")
class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AWS Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET_NAME: str
    AWS_REGION: str = "us-east-1"

    # Server Configuration
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "LearnLab"

    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    NEXT_PUBLIC_API_URL: str
    GOOGLE_API_CREDENTIALS: str
    UPSTASH_VECTOR_REST_URL: str
    UPSTASH_VECTOR_REST_TOKEN: str
    GEMINI_API_KEY: str
    ELEVENLABS_API_KEY: str
    ELEVENLABS_VOICE_ID_1: str
    ELEVENLABS_VOICE_ID_2: str

    # API Configuration
    API_V1_STR: str = "/api/v1"

    # CORS Configuration
    ALLOW_ORIGINS: list[str] = [
        "http://localhost:3000",     # Frontend
        "http://localhost:8000",     # Backend
        "http://localhost:8501"      # Streamlit
    ]
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]

    def get_database_url(self) -> str:
        """
        Get the database URL based on the environment
        """
        return self.DATABASE_URL

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow" 
    )

settings = Settings()