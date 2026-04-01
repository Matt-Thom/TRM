import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TenantBase

class RiskMatrixConfig(TenantBase):
    __tablename__ = "risk_matrix_config"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    likelihood_labels = Column(JSONB, nullable=False, server_default='["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"]')
    impact_labels = Column(JSONB, nullable=False, server_default='["Negligible", "Minor", "Moderate", "Major", "Severe"]')
    thresholds = Column(JSONB, nullable=False, server_default='{"Low": {"min": 1, "max": 4}, "Medium": {"min": 5, "max": 9}, "High": {"min": 10, "max": 16}, "Critical": {"min": 17, "max": 25}}')
