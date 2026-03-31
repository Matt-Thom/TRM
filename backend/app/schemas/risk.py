"""Pydantic schemas for the Risk entity."""

from datetime import datetime
import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.risk import RiskCategory, RiskStatus


class RiskBase(BaseModel):
    """Base fields for Risk schemas."""
    title: str = Field(..., max_length=255)
    description: str
    threat_source: str = Field(..., max_length=255)
    vulnerability: str = Field(..., max_length=255)
    asset_at_risk: Optional[str] = None
    asset_id: Optional[uuid.UUID] = None
    category: RiskCategory
    status: RiskStatus = RiskStatus.OPEN
    likelihood: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)
    risk_owner_id: Optional[uuid.UUID] = None


class RiskCreate(RiskBase):
    """Schema for creating a new Risk."""
    pass


class RiskUpdate(BaseModel):
    """Schema for updating an existing Risk."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    threat_source: Optional[str] = Field(None, max_length=255)
    vulnerability: Optional[str] = Field(None, max_length=255)
    asset_at_risk: Optional[str] = None
    category: Optional[RiskCategory] = None
    status: Optional[RiskStatus] = None
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    impact: Optional[int] = Field(None, ge=1, le=5)
    risk_owner_id: Optional[uuid.UUID] = None


class RiskResponse(RiskBase):
    """Schema for Risk responses."""
    id: uuid.UUID
    tenant_id: uuid.UUID
    inherent_risk_score: int
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskListResponse(BaseModel):
    """Schema for returning a paginated list of risks."""
    items: List[RiskResponse]
    next_cursor: Optional[str] = None
    has_more: bool = False
