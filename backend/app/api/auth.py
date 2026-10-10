import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import LoginRequest, Token, UserResponse
from app.api.deps import verify_password, create_access_token, get_current_user
from app.services.audit_logger import log_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate user and return JWT bearer token."""
    start_time = time.time()
    user = db.query(User).filter(User.email == login_data.email.lower()).first()

    client_ip = request.client.host if request.client else None

    if not user or not verify_password(login_data.password, user.hashed_password):
        log_event(
            db=db,
            tenant_id=user.tenant_id if user else None,
            user_id=user.id if user else None,
            user_email=login_data.email,
            action="login",
            outcome="FORBIDDEN",
            latency_ms=int((time.time() - start_time) * 1000),
            details="Invalid login credentials",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been disabled"
        )

    # Update last login time
    user.last_login_at = datetime.utcnow()
    db.commit()

    tenant_slug = user.tenant.slug if user.tenant else None
    tenant_name = user.tenant.name if user.tenant else None

    # Encode token
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "tenant_slug": tenant_slug
    }
    access_token = create_access_token(data=token_payload)

    log_event(
        db=db,
        tenant_id=user.tenant_id,
        user_id=user.id,
        user_email=user.email,
        action="login",
        outcome="SUCCESS",
        latency_ms=int((time.time() - start_time) * 1000),
        details=f"Successful login for {user.email}",
        ip_address=client_ip
    )

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        tenant_id=user.tenant_id,
        tenant_name=tenant_name,
        tenant_slug=tenant_slug,
        is_active=user.is_active
    )

    return Token(access_token=access_token, token_type="bearer", user=user_resp)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    """Retrieve profile and tenant details of authenticated user."""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        tenant_id=user.tenant_id,
        tenant_name=user.tenant.name if user.tenant else None,
        tenant_slug=user.tenant.slug if user.tenant else None,
        is_active=user.is_active
    )


@router.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Client logout and audit trail recording."""
    log_event(
        db=db,
        tenant_id=user.tenant_id,
        user_id=user.id,
        user_email=user.email,
        action="logout",
        outcome="SUCCESS",
        details="User logged out"
    )
    return {"message": "Successfully logged out"}
