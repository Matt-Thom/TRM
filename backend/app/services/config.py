"""Business logic for Configuration."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.risk_matrix_config import RiskMatrixConfig
from app.schemas.config import RiskMatrixConfigUpdate

DEFAULT_LIKELIHOOD_LABELS = ["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"]
DEFAULT_IMPACT_LABELS = ["Negligible", "Minor", "Moderate", "Major", "Severe"]
DEFAULT_SCORE_THRESHOLDS = {"Low": 4, "Medium": 9, "High": 16, "Critical": 25}

async def get_risk_matrix_config(session: AsyncSession, tenant_id: uuid.UUID) -> Optional[RiskMatrixConfig]:
    """Get the risk matrix config for a tenant."""
    query = select(RiskMatrixConfig).where(RiskMatrixConfig.tenant_id == tenant_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def update_risk_matrix_config(
    session: AsyncSession,
    config_in: RiskMatrixConfigUpdate,
    tenant_id: uuid.UUID
) -> RiskMatrixConfig:
    """Update or create the risk matrix config for a tenant."""
    config = await get_risk_matrix_config(session, tenant_id)

    if config:
        config.likelihood_labels = config_in.likelihood_labels
        config.impact_labels = config_in.impact_labels
        config.score_thresholds = config_in.score_thresholds
    else:
        config = RiskMatrixConfig(
            tenant_id=tenant_id,
            likelihood_labels=config_in.likelihood_labels,
            impact_labels=config_in.impact_labels,
            score_thresholds=config_in.score_thresholds
        )
        session.add(config)

    await session.commit()
    await session.refresh(config)
    return config

async def seed_default_matrix_config(session: AsyncSession, tenant_id: uuid.UUID) -> RiskMatrixConfig:
    """Seed the default risk matrix config for a tenant."""
    config = await get_risk_matrix_config(session, tenant_id)
    if not config:
        config = RiskMatrixConfig(
            tenant_id=tenant_id,
            likelihood_labels=DEFAULT_LIKELIHOOD_LABELS,
            impact_labels=DEFAULT_IMPACT_LABELS,
            score_thresholds=DEFAULT_SCORE_THRESHOLDS
        )
        session.add(config)
        await session.commit()
        await session.refresh(config)
    return config
