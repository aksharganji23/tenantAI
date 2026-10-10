from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TenantBase(BaseModel):
    name: str
    slug: str
    domain: Optional[str] = None
    plan: str = "enterprise"
    quota_docs: int = 100
    quota_queries: int = 5000


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    plan: Optional[str] = None
    quota_docs: Optional[int] = None
    quota_queries: Optional[int] = None
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user_count: int = 0
    document_count: int = 0

    class Config:
        from_attributes = True
