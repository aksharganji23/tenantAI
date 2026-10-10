from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):
    id: int
    chunk_index: int
    content: str
    page_number: int
    token_count: int

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    tenant_id: int
    filename: str
    file_type: str
    file_size: int
    title: str
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []
