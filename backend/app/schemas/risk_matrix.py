from pydantic import BaseModel, ConfigDict
from typing import List, Dict

class ThresholdConfig(BaseModel):
    min: int
    max: int

class Thresholds(BaseModel):
    Low: ThresholdConfig
    Medium: ThresholdConfig
    High: ThresholdConfig
    Critical: ThresholdConfig

class RiskMatrixBase(BaseModel):
    likelihood_labels: List[str]
    impact_labels: List[str]
    thresholds: Thresholds

class RiskMatrixUpdate(RiskMatrixBase):
    pass

class RiskMatrixResponse(RiskMatrixBase):
    model_config = ConfigDict(from_attributes=True)
