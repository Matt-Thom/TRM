"""Treatment model for TRM."""

import uuid
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantBase

class TreatmentState(str, Enum):
    """Enum for risk treatment workflow state."""
    DRAFT = "Draft"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    IMPLEMENTED = "Implemented"

class RiskTreatment(TenantBase, Base):
    """Risk Treatment entity mapping to a Risk."""

    __tablename__ = "risk_treatments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    risk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risks.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[TreatmentState] = mapped_column(String(50), nullable=False, default=TreatmentState.DRAFT)

    # Expected post-treatment scores
    target_likelihood: Mapped[int] = mapped_column(Integer, nullable=False)
    target_impact: Mapped[int] = mapped_column(Integer, nullable=False)
    target_residual_score: Mapped[int] = mapped_column(Integer, nullable=False)

    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    due_date: Mapped[str | None] = mapped_column(String(50), nullable=True) # ISO format date
