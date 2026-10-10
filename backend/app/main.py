from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

from app.config import settings
from app.database import engine, Base, get_db
from app.models import EmailVerificationCode, TelegramSession  # noqa: F401

# Import routers
from app.api.auth import router as auth_router
from app.api.tenants import router as tenants_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.logs import router as logs_router
from app.api.admin import router as admin_router
from app.api.demo import router as demo_router

# Initialize tables
Base.metadata.create_all(bind=engine)


def ensure_compatibility_schema():
    """Add the verification column to databases created before OTP support."""
    columns = {column["name"] for column in inspect(engine).get_columns("users")}
    if "is_verified" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT TRUE")
            )


ensure_compatibility_schema()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Multi-Tenant AI Chatbot Platform with Strict Tenant Isolation, RAG, and Audit Telemetry.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(tenants_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(logs_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
app.include_router(demo_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint validating database connectivity and system status."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app": "TenantAI",
        "version": settings.VERSION,
        "database": db_status,
        "ai_engine": "Gemini-API" if settings.GEMINI_API_KEY else "Local-Grounded-RAG (Deterministic Zero-Cloud)",
        "vector_search": "Cosine Semantic Indexing"
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs"
    }

