"""Request ID middleware for tracing requests across the system."""

import uuid
from contextvars import ContextVar

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable so logging processors can access request_id without threading issues
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request and response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Use incoming header if present (e.g. from a load balancer), otherwise generate
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Make available on request state and in the context variable for logging
        request.state.request_id = request_id
        token = request_id_ctx_var.set(request_id)

        try:
            response: Response = await call_next(request)
        finally:
            request_id_ctx_var.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response
