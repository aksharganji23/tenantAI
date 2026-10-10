from typing import Optional
from sqlalchemy.orm import Session
from app.models.usage_log import UsageLog


def log_event(
    db: Session,
    tenant_id: Optional[int],
    user_id: Optional[int],
    user_email: Optional[str],
    action: str,
    outcome: str = "SUCCESS",
    latency_ms: int = 0,
    tokens_used: int = 0,
    model_name: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
) -> UsageLog:
    """
    Persist an audit and telemetry event to the database.
    Catches errors internally to prevent request failure.
    """
    try:
        log_entry = UsageLog(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=action,
            outcome=outcome,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            model_name=model_name,
            details=details,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        db.rollback()
        print(f"[AuditLogger Error] Failed to write usage log: {e}")
        return None
