from typing import Optional
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    tenant_id: Optional[int] = None
    tenant_name: Optional[str] = None
    tenant_slug: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str  # user id as string
    email: str
    role: str
    tenant_id: Optional[int] = None
    tenant_slug: Optional[str] = None
    exp: Optional[int] = None
