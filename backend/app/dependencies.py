"""FastAPI dependency injection.

Wiring:
  - TASK-1.03: tenant / RLS wiring (get_db_session, get_superadmin_session)
  - TASK-1.05: JWT authentication and user resolution (get_current_user)
"""

from typing import AsyncGenerator

import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import text

from app.db import async_session_factory
from app.services.auth import decode_token

logger = structlog.get_logger(__name__)

security = HTTPBearer()


async def get_db_session(request: Request) -> AsyncGenerator:
    """Yield a tenant-scoped database session with RLS context."""
    async with async_session_factory() as session:
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id:
            await session.execute(
                text(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")
            )
        yield session


async def get_superadmin_session() -> AsyncGenerator:
    """Yield a superadmin database session that bypasses RLS."""
    async with async_session_factory() as session:
        await session.execute(text("SET LOCAL app.is_superadmin = true"))
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Extract and validate the current user from JWT."""
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    return {
        "user_id": payload["sub"],
        "tenant_id": payload["tenant_id"],
        "role": payload["role"],
    }


async def get_tenant_id(request: Request) -> str | None:
    """Return the tenant_id for the current request.

    Reads the value placed on request.state by TenantMiddleware.
    """
    return getattr(request.state, "tenant_id", None)
