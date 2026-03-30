"""Router for risk management endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.models.risk import RiskCategory, RiskStatus
from app.schemas.responses import APIResponse
from app.schemas.risk import RiskCreate, RiskUpdate, RiskResponse, RiskListResponse
from app.services import risk as risk_service

router = APIRouter(prefix="/risks", tags=["Risks"])


@router.post("", response_model=APIResponse[RiskResponse])
async def create_risk(
    risk_in: RiskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new risk."""
    risk = await risk_service.create_risk(session, risk_in, current_user.id)
    return APIResponse(data=RiskResponse.model_validate(risk))


@router.get("", response_model=APIResponse[RiskListResponse])
async def list_risks(
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[str] = None,
    status: Optional[RiskStatus] = None,
    category: Optional[RiskCategory] = None,
    risk_owner_id: Optional[uuid.UUID] = None,
    min_score: Optional[int] = Query(None, ge=1, le=25),
    max_score: Optional[int] = Query(None, ge=1, le=25),
    sort_by: str = Query("inherent_risk_score", regex="^(inherent_risk_score|created_at|updated_at)$"),
    sort_desc: bool = True,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """List risks with filtering, sorting, and cursor-based pagination."""
    risks, next_cursor, has_more = await risk_service.list_risks(
        session=session,
        limit=limit,
        cursor=cursor,
        status=status,
        category=category,
        risk_owner_id=risk_owner_id,
        min_score=min_score,
        max_score=max_score,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    return APIResponse(
        data=RiskListResponse(
            items=[RiskResponse.model_validate(r) for r in risks],
            next_cursor=next_cursor,
            has_more=has_more,
        )
    )


@router.get("/{risk_id}", response_model=APIResponse[RiskResponse])
async def get_risk(
    risk_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Get a risk by ID."""
    risk = await risk_service.get_risk(session, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    return APIResponse(data=RiskResponse.model_validate(risk))


@router.put("/{risk_id}", response_model=APIResponse[RiskResponse])
async def update_risk(
    risk_id: uuid.UUID,
    risk_in: RiskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Update a risk by ID."""
    db_risk = await risk_service.get_risk(session, risk_id)
    if not db_risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    updated_risk = await risk_service.update_risk(session, db_risk, risk_in)
    return APIResponse(data=RiskResponse.model_validate(updated_risk))


@router.delete("/{risk_id}", response_model=APIResponse[None])
async def delete_risk(
    risk_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a risk by ID."""
    await risk_service.delete_risk(session, risk_id)
    return APIResponse(data=None)
