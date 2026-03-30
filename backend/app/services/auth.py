"""Authentication service for local auth (Argon2 + JWT)."""

import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.models.user_tenant_role import UserTenantRole

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return ph.hash(password)


def verify_password(password: str, hash: str) -> bool:
    """Verify a password against an Argon2 hash."""
    try:
        return ph.verify(hash, password)
    except VerifyMismatchError:
        return False


def create_access_token(user_id: str, tenant_id: str, role: str) -> str:
    """Create a JWT access token with user, tenant, and role claims."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(seconds=settings.JWT_ACCESS_TOKEN_TTL),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=settings.JWT_REFRESH_TOKEN_TTL),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises JWTError on invalid tokens."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.

    Returns the User if credentials are valid, None otherwise.
    Uses constant-time comparison to prevent timing attacks.
    """
    # Use superadmin context to find user across tenants
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or user.password_hash is None:
        # Perform a dummy hash to prevent timing-based user enumeration
        ph.hash("dummy-password-for-timing")
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user


async def get_user_tenant_role(session: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID | None = None) -> UserTenantRole | None:
    """
    Get the user's role for a specific tenant, or their first tenant if none specified.
    """
    query = select(UserTenantRole).where(UserTenantRole.user_id == user_id)
    if tenant_id:
        query = query.where(UserTenantRole.tenant_id == tenant_id)

    result = await session.execute(query)
    return result.scalar_one_or_none()
