import os
import json
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TenantAI - Secure Multi-Tenant AI Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tenantai.db")

    # Security & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Email verification
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    OTP_MAX_RESENDS_PER_HOUR: int = 5

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
        "http://127.0.0.1:8000"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

raw_cors_origins = os.getenv("CORS_ORIGINS")
if raw_cors_origins:
    try:
        parsed_origins = json.loads(raw_cors_origins)
        settings.CORS_ORIGINS = parsed_origins if isinstance(parsed_origins, list) else [raw_cors_origins]
    except json.JSONDecodeError:
        settings.CORS_ORIGINS = [origin.strip() for origin in raw_cors_origins.split(",") if origin.strip()]

if "*" in settings.CORS_ORIGINS:
    raise RuntimeError("Wildcard CORS origins are not allowed when credentials are enabled")

if not settings.SECRET_KEY:
    if settings.ENVIRONMENT.lower() == "production":
        raise RuntimeError("SECRET_KEY must be configured in production")
    settings.SECRET_KEY = "local-development-only-change-me"
elif settings.ENVIRONMENT.lower() == "production" and len(settings.SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY must contain at least 32 characters in production")

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
