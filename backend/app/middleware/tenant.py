"""Tenant context middleware — stub implementation."""

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Extract tenant context from the request and make it available downstream.

    Full implementation lives in TASK-1.03; this stub simply passes through
    so the rest of the stack can reference request.state.tenant_id without
    errors during early development.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # TODO(TASK-1.03): Decode JWT, extract tenant_id claim, and set the
        # PostgreSQL session variable for Row Level Security (RLS):
        #   SET LOCAL app.tenant_id = '<tenant_id>';
        # For now we just set a sentinel value so downstream code can check
        # for None rather than catching AttributeError.
        request.state.tenant_id = None

        response: Response = await call_next(request)
        return response
