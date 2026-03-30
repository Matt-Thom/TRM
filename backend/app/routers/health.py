"""Health check router — verifies database and Redis connectivity."""

import structlog
from fastapi import APIRouter, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

import redis.asyncio as aioredis

from app.config import settings
from app.schemas.responses import APIResponse, Meta

router = APIRouter(prefix="/api/v1", tags=["health"])
logger = structlog.get_logger(__name__)


@router.get("/health", response_model=APIResponse[dict])
async def health_check(request: Request) -> APIResponse[dict]:
    """Return the operational status of the service and its dependencies."""
    request_id: str = getattr(request.state, "request_id", None)

    # --- Database ping ---
    db_status = "disconnected"
    try:
        engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        db_status = "connected"
    except Exception as exc:
        logger.warning("health_check.db_ping_failed", error=str(exc), request_id=request_id)

    # --- Redis ping ---
    redis_status = "disconnected"
    try:
        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        await client.ping()
        await client.aclose()
        redis_status = "connected"
    except Exception as exc:
        logger.warning("health_check.redis_ping_failed", error=str(exc), request_id=request_id)

    return APIResponse(
        data={"status": "healthy", "database": db_status, "redis": redis_status},
        meta=Meta(request_id=request_id),
        errors=[],
    )
