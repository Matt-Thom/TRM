"""Authentication endpoints for local auth."""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.responses import APIResponse, ErrorDetail, Meta
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_tenant_role,
    hash_password,
)
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_tenant_role import UserTenantRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# Dependency: get a superadmin DB session (bypasses RLS for auth operations)
async def get_auth_session():
    """Get a DB session with superadmin privileges for auth operations."""
    from app.db import async_session_factory
    async with async_session_factory() as session:
        await session.execute(text("SET LOCAL app.is_superadmin = true"))
        yield session


@router.post("/register")
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_auth_session),
):
    """Register a new user under a specific tenant."""
    # Find tenant by slug
    result = await session.execute(
        select(Tenant).where(Tenant.slug == body.tenant_slug, Tenant.is_active == True)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant",
        )

    # Check if email already exists
    existing = await session.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
    )
    session.add(user)
    await session.flush()

    # Assign user to tenant with viewer role (default for new registrations)
    role = UserTenantRole(
        user_id=user.id,
        tenant_id=tenant.id,
        role="viewer",
    )
    session.add(role)
    await session.commit()

    # Generate tokens
    access_token = create_access_token(str(user.id), str(tenant.id), "viewer")
    refresh_token = create_refresh_token(str(user.id))

    return APIResponse(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        meta=Meta(),
    )


@router.post("/login")
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_auth_session),
):
    """Authenticate with email and password."""
    user = await authenticate_user(session, body.email, body.password)

    if not user:
        # Same error for wrong email or wrong password — no info leakage
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Get user's tenant role
    tenant_role = await get_user_tenant_role(session, user.id)
    if not tenant_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assignment",
        )

    access_token = create_access_token(
        str(user.id), str(tenant_role.tenant_id), tenant_role.role
    )
    refresh_token = create_refresh_token(str(user.id))

    return APIResponse(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        meta=Meta(),
    )


@router.post("/refresh")
async def refresh_token(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_auth_session),
):
    """Refresh an access token using a refresh token."""
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    result = await session.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    tenant_role = await get_user_tenant_role(session, user.id)
    if not tenant_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant assignment",
        )

    access_token = create_access_token(
        str(user.id), str(tenant_role.tenant_id), tenant_role.role
    )
    new_refresh_token = create_refresh_token(str(user.id))

    return APIResponse(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        ),
        meta=Meta(),
    )
