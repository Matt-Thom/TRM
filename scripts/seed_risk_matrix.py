import asyncio
import os
import sys

# Add the backend directory to sys.path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.models.tenant import Tenant
from app.models.risk_matrix import RiskMatrixConfig

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://temper:temper@localhost:5432/temper",
)

async def seed_matrix():
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Get all tenants
        result = await session.execute(select(Tenant))
        tenants = result.scalars().all()

        for tenant in tenants:
            # Check if matrix already exists
            matrix_result = await session.execute(
                select(RiskMatrixConfig).where(RiskMatrixConfig.tenant_id == tenant.id)
            )
            matrix = matrix_result.scalar_one_or_none()

            if not matrix:
                print(f"Creating default risk matrix config for tenant {tenant.name} ({tenant.id})")
                new_matrix = RiskMatrixConfig(
                    tenant_id=tenant.id,
                    likelihood_labels=["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"],
                    impact_labels=["Negligible", "Minor", "Moderate", "Major", "Severe"],
                    thresholds={
                        "Low": {"min": 1, "max": 4},
                        "Medium": {"min": 5, "max": 9},
                        "High": {"min": 10, "max": 16},
                        "Critical": {"min": 17, "max": 25}
                    }
                )
                session.add(new_matrix)

        await session.commit()

    await engine.dispose()
    print("Risk matrix seeding completed.")

if __name__ == "__main__":
    asyncio.run(seed_matrix())
