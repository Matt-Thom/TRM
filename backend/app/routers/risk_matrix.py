import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_db_session
from app.dependencies import get_current_user
from app.models.risk_matrix import RiskMatrixConfig
from app.models.user import User
from app.models.user_tenant_role import UserTenantRole
from app.schemas.responses import APIResponse
from app.schemas.risk_matrix import RiskMatrixResponse, RiskMatrixUpdate

router = APIRouter(prefix="/api/v1/config/risk-matrix", tags=["Config"])


@router.get("", response_model=APIResponse[RiskMatrixResponse])
async def get_risk_matrix(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """Get the current risk matrix configuration."""
    result = await db.execute(select(RiskMatrixConfig))
    matrix = result.scalar_one_or_none()

    if not matrix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk matrix configuration not found for this tenant.",
        )

    return APIResponse(data=RiskMatrixResponse.model_validate(matrix))


@router.put("", response_model=APIResponse[RiskMatrixResponse])
async def update_risk_matrix(
    update_data: RiskMatrixUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Any:
    """Update the current risk matrix configuration. Admin only."""

    # Check if current_user has 'admin' role in the current tenant context.
    # Note: Tenant context logic has already filtered `user_tenant_roles` to the active tenant.
    role_result = await db.execute(select(UserTenantRole).where(UserTenantRole.user_id == current_user.id))
    user_role = role_result.scalar_one_or_none()

    if not user_role or user_role.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update the risk matrix.",
        )

    # Validate 5x5 grid constraint
    if len(update_data.likelihood_labels) != 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="likelihood_labels must have exactly 5 items")
    if len(update_data.impact_labels) != 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="impact_labels must have exactly 5 items")

    result = await db.execute(select(RiskMatrixConfig))
    matrix = result.scalar_one_or_none()

    if not matrix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk matrix configuration not found for this tenant.",
        )

    matrix.likelihood_labels = update_data.likelihood_labels
    matrix.impact_labels = update_data.impact_labels
    matrix.thresholds = update_data.thresholds.model_dump()

    db.add(matrix)
    await db.commit()
    await db.refresh(matrix)

    return APIResponse(data=RiskMatrixResponse.model_validate(matrix))
