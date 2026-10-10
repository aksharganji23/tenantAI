from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usage_log import UsageLog
from app.models.user import User
from app.schemas.admin import UsageLogResponse
from app.api.deps import get_current_tenant_id, require_tenant_admin

router = APIRouter(prefix="/logs", tags=["Audit Logs"])


@router.get("", response_model=List[UsageLogResponse])
def get_usage_logs(
    action: Optional[str] = Query(None),
    outcome: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_tenant_admin),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Retrieve audit and telemetry logs strictly scoped to current tenant.
    Superadmins can see all logs if tenant_id is 1 or overridden.
    """
    query = db.query(UsageLog)

    if current_user.role != "superadmin":
        query = query.filter(UsageLog.tenant_id == tenant_id)
    else:
        # Superadmin can view tenant-specific or global
        if tenant_id:
            query = query.filter(UsageLog.tenant_id == tenant_id)

    if action:
        query = query.filter(UsageLog.action == action)
    if outcome:
        query = query.filter(UsageLog.outcome == outcome)

    logs = query.order_by(UsageLog.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for log in logs:
        t_name = log.tenant.name if log.tenant else ("Global" if log.tenant_id is None else None)
        item = UsageLogResponse.model_validate(log)
        item.tenant_name = t_name
        # Keep the audit view useful without exposing prompt contents, user
        # identities, or network identifiers through a broad admin endpoint.
        item.user_email = None
        item.ip_address = None
        if item.action == "chat_query":
            item.details = "Chat query completed"
        results.append(item)

    return results
