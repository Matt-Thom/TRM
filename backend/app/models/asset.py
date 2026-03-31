"""Asset model for TRM."""

import uuid
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantBase

class Asset(TenantBase, Base):
    """Configuration Item (Asset) synced from ConnectWise."""

    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cw_configuration_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type_name: Mapped[str] = mapped_column(String(100), nullable=True)
    status_name: Mapped[str] = mapped_column(String(100), nullable=True)
