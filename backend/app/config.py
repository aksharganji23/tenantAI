import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TenantAI - Secure Multi-Tenant AI Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tenantai.db")

    # Security & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tenantai-super-secret-jwt-encryption-key-hackathon-2025")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # AI Configuration (Optional live API keys; local fallback active if omitted)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    EMBEDDING_MODEL: str = "text-embedding-004"
    LLM_MODEL: str = "gemini-1.5-flash"

    # Storage & Upload Limits
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage")
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "md"]

    # RAG Tuning
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 120
    SIMILARITY_THRESHOLD: float = 0.25
    TOP_K_CHUNKS: int = 4

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
