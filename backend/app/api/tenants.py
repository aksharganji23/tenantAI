from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tenant import Tenant
from app.models.document import Document
from app.models.user import User
from app.schemas.tenant import TenantResponse, TenantUpdate
from app.api.deps import get_current_user, get_current_tenant_id, require_superadmin, require_tenant_admin

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("/current", response_model=TenantResponse)
def get_current_tenant(
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Retrieve metadata and quotas for the authenticated user's workspace."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant workspace not found")

    user_count = db.query(User).filter(User.tenant_id == tenant_id).count()
    doc_count = db.query(Document).filter(Document.tenant_id == tenant_id).count()

    resp = TenantResponse.model_validate(tenant)
    resp.user_count = user_count
    resp.document_count = doc_count
    return resp


@router.patch("/current", response_model=TenantResponse)
def update_current_tenant(
    data: TenantUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    current_user: User = Depends(require_tenant_admin),
    db: Session = Depends(get_db)
):
    """Update workspace settings (restricted to Tenant Admins)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant workspace not found")

    if data.name is not None:
        tenant.name = data.name
    if data.domain is not None:
        tenant.domain = data.domain

    db.commit()
    db.refresh(tenant)

    user_count = db.query(User).filter(User.tenant_id == tenant_id).count()
    doc_count = db.query(Document).filter(Document.tenant_id == tenant_id).count()

    resp = TenantResponse.model_validate(tenant)
    resp.user_count = user_count
    resp.document_count = doc_count
    return resp


@router.get("", response_model=List[TenantResponse])
def list_all_tenants(
    admin: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """List all tenant workspaces (restricted to Superadmin)."""
    tenants = db.query(Tenant).all()
    results = []
    for t in tenants:
        u_count = db.query(User).filter(User.tenant_id == t.id).count()
        d_count = db.query(Document).filter(Document.tenant_id == t.id).count()
        t_resp = TenantResponse.model_validate(t)
        t_resp.user_count = u_count
        t_resp.document_count = d_count
        results.append(t_resp)
    return results
