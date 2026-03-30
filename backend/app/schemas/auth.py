"""Authentication request and response schemas."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str
    tenant_slug: str  # Which tenant to register under


class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_slug: str | None = None  # Optional: specify tenant for multi-tenant users


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    tenant_id: str
    role: str
