from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.tenant import TenantResponse


class PlatformStatsResponse(BaseModel):
    total_tenants: int
    total_users: int
    total_documents: int
    total_queries: int
    total_tokens: int
    active_tenants: int
    failed_documents: int


class TenantUsageSummary(BaseModel):
    tenant_id: int
    tenant_name: str
    tenant_slug: str
    documents_count: int
    queries_count: int
    total_tokens: int
    last_active: Optional[datetime] = None


class UsageLogResponse(BaseModel):
    id: int
    tenant_id: Optional[int] = None
    tenant_name: Optional[str] = None
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    outcome: str
    latency_ms: int
    tokens_used: int
    model_name: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CrossTenantSimulationResult(BaseModel):
    simulation_name: str
    attacker_tenant: str
    target_tenant: str
    attempted_resource_type: str
    resource_id: int
    http_status: int
    is_blocked: bool
    data_leaked: bool
    audit_logged: bool
    explanation: str
