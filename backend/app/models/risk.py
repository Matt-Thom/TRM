"""Risk model for TRM."""

import uuid
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantBase

class RiskCategory(str, Enum):
    """Enum for risk categories."""
    ORGANISATIONAL = "Organisational"
    PEOPLE = "People"
    PHYSICAL = "Physical"
    TECHNOLOGICAL = "Technological"

class RiskStatus(str, Enum):
    """Enum for risk status."""
    OPEN = "Open"
    UNDER_REVIEW = "Under Review"
    MITIGATED = "Mitigated"
    ACCEPTED = "Accepted"
    CLOSED = "Closed"

class Risk(TenantBase, Base):
    """Risk entity."""

    __tablename__ = "risks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    threat_source: Mapped[str] = mapped_column(String(255), nullable=False)
    vulnerability: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_at_risk: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[RiskCategory] = mapped_column(String(50), nullable=False)
    status: Mapped[RiskStatus] = mapped_column(String(50), nullable=False, default=RiskStatus.OPEN)
    likelihood: Mapped[int] = mapped_column(Integer, nullable=False)
    impact: Mapped[int] = mapped_column(Integer, nullable=False)
    inherent_risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
