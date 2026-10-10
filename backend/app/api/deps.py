from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import TokenPayload

security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Secure bcrypt password check."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and verify the current authenticated user from JWT token.
    Raises 401 if unauthenticated or token is invalid.
    """
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            auth.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        user_id = int(user_id_str)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_tenant_id(
    user: User = Depends(get_current_user),
    x_tenant_override: Optional[str] = Header(None, alias="X-Tenant-Override")
) -> int:
    """
    STRICT TENANT RESOLVER:
    Resolves authorized tenant ID derived strictly from trusted authentication state.
    Only superadmins can use X-Tenant-Override for administrative diagnostics.
    Regular tenant users are locked to their user.tenant_id.
    """
    if user.role == "superadmin":
        if x_tenant_override:
            try:
                return int(x_tenant_override)
            except ValueError:
                pass
        # Default superadmin to first active tenant or tenant_id if assigned
        return user.tenant_id or 1

    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to any tenant workspace"
        )

    return user.tenant_id


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    """Restrict access to system-level administrators."""
    if user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires Superadmin administrative privileges"
        )
    return user


def require_tenant_admin(user: User = Depends(get_current_user)) -> User:
    """Restrict access to Tenant Admins or Superadmin."""
    if user.role not in ("superadmin", "tenant_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires Tenant Admin privileges"
        )
    return user
