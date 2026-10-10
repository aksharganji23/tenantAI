import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.email_verification import EmailVerificationCode
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    ResendVerificationRequest,
    Token,
    UserResponse,
    VerifyEmailRequest,
)
from app.api.deps import verify_password, create_access_token, get_current_user, get_password_hash
from app.config import settings
from app.services.email_sender import send_verification_code
from app.services.audit_logger import log_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _hash_otp(otp: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        otp.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _issue_verification_code(user: User, db: Session) -> None:
    now = datetime.utcnow()
    recent = (
        db.query(EmailVerificationCode)
        .filter(
            EmailVerificationCode.user_id == user.id,
            EmailVerificationCode.created_at >= now - timedelta(hours=1),
        )
        .count()
    )
    if recent >= settings.OTP_MAX_RESENDS_PER_HOUR:
        raise HTTPException(status_code=429, detail="Too many verification emails. Try again later.")

    latest = (
        db.query(EmailVerificationCode)
        .filter(EmailVerificationCode.user_id == user.id)
        .order_by(EmailVerificationCode.created_at.desc())
        .first()
    )
    if latest and (now - latest.created_at).total_seconds() < settings.OTP_RESEND_COOLDOWN_SECONDS:
        raise HTTPException(status_code=429, detail="Please wait before requesting another code.")

    otp = f"{secrets.randbelow(1_000_000):06d}"
    challenge = EmailVerificationCode(
        user_id=user.id,
        code_hash=_hash_otp(otp),
        expires_at=now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        attempts=0,
        consumed=False,
        last_sent_at=now,
    )
    db.add(challenge)
    db.commit()
    try:
        send_verification_code(user.email, otp)
    except Exception:
        db.delete(challenge)
        db.commit()
        raise HTTPException(status_code=503, detail="Email delivery is unavailable. Please try again later.")


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Create a pending tenant and send its administrator an email OTP."""
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    if db.query(Tenant).filter(Tenant.slug == data.company_slug).first():
        raise HTTPException(status_code=409, detail="That company URL is already registered.")

    tenant = Tenant(name=data.company_name.strip(), slug=data.company_slug)
    db.add(tenant)
    db.flush()
    user = User(
        email=email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name.strip(),
        role="tenant_admin",
        tenant_id=tenant.id,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _issue_verification_code(user, db)
    return {"message": "Verification code sent.", "email": user.email, "expires_in_seconds": settings.OTP_EXPIRY_MINUTES * 60}


@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification request.")
    if user.is_verified:
        return {"message": "Email is already verified."}
    challenge = (
        db.query(EmailVerificationCode)
        .filter(
            EmailVerificationCode.user_id == user.id,
            EmailVerificationCode.consumed.is_(False),
        )
        .order_by(EmailVerificationCode.created_at.desc())
        .first()
    )
    if not challenge or challenge.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="This verification code has expired.")
    if challenge.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many incorrect attempts. Request a new code.")
    challenge.attempts += 1
    if not hmac.compare_digest(challenge.code_hash, _hash_otp(data.otp)):
        db.commit()
        raise HTTPException(status_code=400, detail="Incorrect verification code.")
    challenge.consumed = True
    user.is_verified = True
    db.commit()
    return {"message": "Email verified. You can now sign in."}


@router.post("/resend-verification")
def resend_verification(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="No pending account was found for that email.")
    if user.is_verified:
        return {"message": "Email is already verified."}
    _issue_verification_code(user, db)
    return {"message": "Verification code sent.", "expires_in_seconds": settings.OTP_EXPIRY_MINUTES * 60}


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
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before signing in.")

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
        is_active=user.is_active,
        is_verified=user.is_verified,
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
        is_active=user.is_active,
        is_verified=user.is_verified,
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
