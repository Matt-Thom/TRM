"""Pydantic schemas for the configuration models."""

import uuid
from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field

class RiskMatrixConfigBase(BaseModel):
    """Base fields for RiskMatrixConfig schemas."""
    likelihood_labels: List[str] = Field(..., min_length=5, max_length=5)
    impact_labels: List[str] = Field(..., min_length=5, max_length=5)
    score_thresholds: Dict[str, int] = Field(...)

class RiskMatrixConfigUpdate(RiskMatrixConfigBase):
    """Schema for updating the RiskMatrixConfig."""
    pass

class RiskMatrixConfigResponse(RiskMatrixConfigBase):
    """Schema for RiskMatrixConfig response."""
    id: uuid.UUID
    tenant_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
