"""Celery tasks for ConnectWise integration."""

import logging
import asyncio
from sqlalchemy import select, update
import uuid

from app.worker import celery_app
from app.config import settings
from app.integrations.connectwise import ConnectWiseClient
from app.models.tenant import Tenant
from app.models.asset import Asset
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)

async_engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

@celery_app.task(name="sync_cw_assets")
def sync_cw_assets_task():
    """Background task to sync ConnectWise assets across all active tenants."""
    logger.info("Starting ConnectWise asset sync...")

    async def _sync_logic():
        async with AsyncSessionLocal() as session:
            # 1. Fetch all tenants with CW configured (Assuming settings apply globally for MVP)
            # In a real multi-tenant scenario, we'd fetch tenant-specific CW API keys
            result = await session.execute(select(Tenant.id))
            tenants = result.scalars().all()

            cw_client = ConnectWiseClient()

            for tenant_id in tenants:
                logger.info(f"Syncing CW assets for tenant {tenant_id}")

                # Fetch CIs from ConnectWise (Sync)
                # In a real scenario, loop pages until empty
                configurations = cw_client.get_configurations_sync(page_size=100)

                if not configurations:
                    logger.warning(f"No CW assets found or CW disabled for tenant {tenant_id}")
                    continue

                for config in configurations:
                    cw_id = config.get("id")
                    name = config.get("name", "Unknown Device")

                    type_name = None
                    type_obj = config.get("type")
                    if isinstance(type_obj, dict):
                        type_name = type_obj.get("name")

                    status_name = None
                    status_obj = config.get("status")
                    if isinstance(status_obj, dict):
                        status_name = status_obj.get("name")

                    # Check if asset exists
                    res = await session.execute(
                        select(Asset)
                        .where(Asset.tenant_id == tenant_id)
                        .where(Asset.cw_configuration_id == cw_id)
                    )
                    existing_asset = res.scalar_one_or_none()

                    if existing_asset:
                        # Update
                        existing_asset.name = name
                        existing_asset.type_name = type_name
                        existing_asset.status_name = status_name
                    else:
                        # Create
                        new_asset = Asset(
                            tenant_id=tenant_id,
                            cw_configuration_id=cw_id,
                            name=name,
                            type_name=type_name,
                            status_name=status_name
                        )
                        session.add(new_asset)

                await session.commit()

        logger.info("ConnectWise asset sync complete.")
        return True

    return asyncio.run(_sync_logic())
