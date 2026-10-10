from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Citation(BaseModel):
    document_id: int
    document_title: str
    page_number: int
    chunk_index: int
    excerpt: str
    score: float


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    top_k: Optional[int] = 4


class ChatResponse(BaseModel):
    message_id: int
    conversation_id: int
    role: str = "assistant"
    content: str
    citations: List[Citation] = []
    confidence_score: Optional[float] = None
    latency_ms: int = 0
    tokens_used: int = 0
    is_grounded: bool = True
    model_name: str = "Grounded-RAG"


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender: str
    content: str
    citations: Optional[List[Citation]] = None
    confidence_score: Optional[float] = None
    latency_ms: Optional[int] = None
    tokens_used: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True
