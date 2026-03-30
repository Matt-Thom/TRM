"""FastAPI dependency injection stubs.

Full implementations are introduced in later tasks:
  - TASK-1.03: tenant / RLS wiring
  - TASK-1.05: JWT authentication and user resolution
"""

from typing import AsyncGenerator

import structlog
from fastapi import Request

logger = structlog.get_logger(__name__)


async def get_db_session() -> AsyncGenerator:
    """Yield a SQLAlchemy AsyncSession.

    TODO(TASK-1.05): Replace with a real session factory that binds to the
    engine configured in config.py and handles commit / rollback on scope exit.
    """
    # Stub: yields nothing so callers that type-hint Optional[AsyncSession]
    # will receive None gracefully during early development.
    yield None  # type: ignore[misc]


async def get_current_user(request: Request):
    """Return the authenticated user for the current request.

    TODO(TASK-1.05): Decode the Bearer JWT from the Authorization header,
    validate claims, and return the corresponding User ORM instance.
    """
    return None


async def get_tenant_id(request: Request) -> str | None:
    """Return the tenant_id for the current request.

    Reads the value placed on request.state by TenantMiddleware.

    TODO(TASK-1.03): Ensure TenantMiddleware correctly populates tenant_id
    from JWT claims before this dependency is used in protected routes.
    """
    return getattr(request.state, "tenant_id", None)
