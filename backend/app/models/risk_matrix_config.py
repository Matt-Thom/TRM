"""Risk Matrix Configuration model for TRM."""

import uuid
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantBase


class RiskMatrixConfig(TenantBase, Base):
    """Tenant-scoped configuration for the qualitative risk scoring matrix."""

    __tablename__ = "risk_matrix_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Expected: list of 5 strings (1=Lowest, 5=Highest)
    likelihood_labels: Mapped[list[str]] = mapped_column(JSONB, nullable=False)

    # Expected: list of 5 strings (1=Lowest, 5=Highest)
    impact_labels: Mapped[list[str]] = mapped_column(JSONB, nullable=False)

    # Expected: dict mapping 'Low', 'Medium', 'High', 'Critical' to their maximum score (inclusive)
    # e.g. {"Low": 4, "Medium": 9, "High": 16, "Critical": 25}
    score_thresholds: Mapped[dict[str, int]] = mapped_column(JSONB, nullable=False)
