"""Router for configuration endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.schemas.responses import APIResponse
from app.schemas.config import RiskMatrixConfigResponse, RiskMatrixConfigUpdate
from app.services import config as config_service

router = APIRouter(prefix="/api/v1/config", tags=["Configuration"])


@router.get("/risk-matrix", response_model=APIResponse[RiskMatrixConfigResponse])
async def get_risk_matrix(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Get the current risk matrix configuration for the tenant."""
    # Ensure current user is linked to a tenant
    tenant_roles = await current_user.awaitable_attrs.tenant_roles
    if not tenant_roles:
        raise HTTPException(status_code=403, detail="User is not associated with any tenant.")

    tenant_id = tenant_roles[0].tenant_id

    config = await config_service.get_risk_matrix_config(session, tenant_id)
    if not config:
        # Seed default if not exists
        config = await config_service.seed_default_matrix_config(session, tenant_id)

    return APIResponse(data=RiskMatrixConfigResponse.model_validate(config))


@router.put("/risk-matrix", response_model=APIResponse[RiskMatrixConfigResponse])
async def update_risk_matrix(
    config_in: RiskMatrixConfigUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Update the risk matrix configuration for the tenant."""
    # Verify user is an admin for the tenant
    tenant_roles = await current_user.awaitable_attrs.tenant_roles
    if not tenant_roles:
        raise HTTPException(status_code=403, detail="User is not associated with any tenant.")

    role = tenant_roles[0].role
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update risk matrix configuration.")

    tenant_id = tenant_roles[0].tenant_id
    config = await config_service.update_risk_matrix_config(session, config_in, tenant_id)

    return APIResponse(data=RiskMatrixConfigResponse.model_validate(config))
