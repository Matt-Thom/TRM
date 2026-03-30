"""Business logic for Risks."""

import uuid
from typing import Optional, Tuple, List
from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.risk import Risk, RiskStatus, RiskCategory
from app.schemas.risk import RiskCreate, RiskUpdate

async def calculate_inherent_risk_score(likelihood: int, impact: int) -> int:
    """Calculates inherent risk score (multiplicative)."""
    return likelihood * impact

async def create_risk(session: AsyncSession, risk_in: RiskCreate, created_by: uuid.UUID) -> Risk:
    """Create a new risk."""
    risk = Risk(**risk_in.model_dump())
    risk.created_by = created_by
    risk.inherent_risk_score = await calculate_inherent_risk_score(risk.likelihood, risk.impact)

    session.add(risk)
    await session.commit()
    await session.refresh(risk)
    return risk

async def get_risk(session: AsyncSession, risk_id: uuid.UUID) -> Optional[Risk]:
    """Get a risk by ID."""
    query = select(Risk).where(Risk.id == risk_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def list_risks(
    session: AsyncSession,
    limit: int = 50,
    cursor: Optional[str] = None,
    status: Optional[RiskStatus] = None,
    category: Optional[RiskCategory] = None,
    risk_owner_id: Optional[uuid.UUID] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    sort_by: str = "inherent_risk_score",
    sort_desc: bool = True
) -> Tuple[List[Risk], Optional[str], bool]:
    """List risks with filtering, sorting, and cursor pagination."""
    query = select(Risk)

    if status:
        query = query.where(Risk.status == status)
    if category:
        query = query.where(Risk.category == category)
    if risk_owner_id:
        query = query.where(Risk.risk_owner_id == risk_owner_id)
    if min_score is not None:
        query = query.where(Risk.inherent_risk_score >= min_score)
    if max_score is not None:
        query = query.where(Risk.inherent_risk_score <= max_score)

    sort_col = getattr(Risk, sort_by, Risk.inherent_risk_score)
    if sort_desc:
        query = query.order_by(desc(sort_col), desc(Risk.id))
    else:
        query = query.order_by(asc(sort_col), desc(Risk.id))

    if cursor:
        try:
            # Simple cursor implementation using Risk ID as cursor
            cursor_uuid = uuid.UUID(cursor)
            if sort_desc:
                query = query.where(Risk.id < cursor_uuid)
            else:
                query = query.where(Risk.id > cursor_uuid)
        except ValueError:
            pass

    query = query.limit(limit + 1)
    result = await session.execute(query)
    risks = list(result.scalars().all())

    has_more = len(risks) > limit
    if has_more:
        risks = risks[:limit]
        next_cursor = str(risks[-1].id)
    else:
        next_cursor = None

    return risks, next_cursor, has_more

async def update_risk(session: AsyncSession, db_risk: Risk, risk_in: RiskUpdate) -> Risk:
    """Update an existing risk."""
    update_data = risk_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_risk, field, value)

    if "likelihood" in update_data or "impact" in update_data:
        db_risk.inherent_risk_score = await calculate_inherent_risk_score(db_risk.likelihood, db_risk.impact)

    await session.commit()
    await session.refresh(db_risk)
    return db_risk

async def delete_risk(session: AsyncSession, risk_id: uuid.UUID) -> None:
    """Delete a risk."""
    risk = await get_risk(session, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    await session.delete(risk)
    await session.commit()
