"""FastAPI application factory for Temper Risk Management."""

import logging
import sys

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.middleware.request_id import RequestIDMiddleware, request_id_ctx_var
from app.middleware.tenant import TenantMiddleware
from app.routers import health
from app.routers import auth
from app.routers import risks
from app.schemas.responses import APIResponse, ErrorDetail, Meta

# ---------------------------------------------------------------------------
# Structlog configuration
# ---------------------------------------------------------------------------

def _configure_logging() -> None:
    """Set up structlog with JSON output and request_id injection."""

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        # Inject request_id from the context variable into every log record.
        _inject_request_id,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.DEBUG:
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Also route stdlib logging through structlog so third-party libraries
    # (SQLAlchemy, uvicorn, etc.) emit structured output.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
    )


def _inject_request_id(logger, method_name, event_dict):  # noqa: ANN001
    """Structlog processor that pulls request_id from the context variable."""
    rid = request_id_ctx_var.get("")
    if rid:
        event_dict["request_id"] = rid
    return event_dict


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    _configure_logging()

    log = structlog.get_logger(__name__)

    app = FastAPI(
        title="Temper Risk Management API",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # --- Middleware (order matters: first added = outermost wrapper) ---

    # CORS must wrap everything so pre-flight OPTIONS requests are handled first.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID before Tenant so tenant middleware can log with a request_id.
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(TenantMiddleware)

    # --- Exception handlers ---

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        body = APIResponse(
            data=None,
            meta=Meta(request_id=request_id),
            errors=[ErrorDetail(code=f"HTTP_{exc.status_code}", message=str(exc.detail))],
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        errors = [
            ErrorDetail(
                code="VALIDATION_ERROR",
                message=err.get("msg", "Invalid value"),
                field=".".join(str(loc) for loc in err.get("loc", [])),
            )
            for err in exc.errors()
        ]
        body = APIResponse(
            data=None,
            meta=Meta(request_id=request_id),
            errors=errors,
        )
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        log.exception(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            request_id=request_id,
        )
        body = APIResponse(
            data=None,
            meta=Meta(request_id=request_id),
            errors=[ErrorDetail(code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred.")],
        )
        return JSONResponse(status_code=500, content=body.model_dump())

    # --- Routers ---
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(risks.router)

    # --- Startup event ---
    @app.on_event("startup")
    async def on_startup() -> None:
        log.info("TRM Backend starting", env=settings.APP_ENV, debug=settings.DEBUG)

    return app


app = create_app()
