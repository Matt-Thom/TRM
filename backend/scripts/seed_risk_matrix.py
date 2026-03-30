import asyncio
import logging
from sqlalchemy import select
from app.db import async_session_factory
from app.models.tenant import Tenant
from app.services.config import seed_default_matrix_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting seed script for risk matrix configs...")
    async with async_session_factory() as session:
        # Get all tenants
        result = await session.execute(select(Tenant.id))
        tenant_ids = result.scalars().all()

        for tenant_id in tenant_ids:
            logger.info(f"Seeding config for tenant: {tenant_id}")
            await seed_default_matrix_config(session, tenant_id)

        logger.info("Seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
