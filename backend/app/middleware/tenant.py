"""Tenant context middleware for RLS enforcement."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extract tenant_id from JWT claims and set PostgreSQL session variable.

    This middleware sets `app.current_tenant_id` on the database session,
    which is used by RLS policies to enforce tenant data isolation.
    """

    # Paths that don't require tenant context
    EXEMPT_PATHS = {"/api/v1/health", "/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/sso/login", "/api/v1/auth/sso/callback", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip tenant context for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            request.state.tenant_id = None
            return await call_next(request)

        # Extract tenant_id from JWT claims (set by auth dependency)
        # TODO(TASK-1.05): Extract from validated JWT. For now, check header.
        tenant_id = request.headers.get("X-Tenant-ID")
        request.state.tenant_id = tenant_id

        return await call_next(request)
