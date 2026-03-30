"""UserTenantRole model — junction table linking users to tenants with a role."""

import uuid
import enum

from sqlalchemy import Enum, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RoleEnum(str, enum.Enum):
    """Roles a user can hold within a tenant."""

    admin = "admin"
    manager = "manager"
    viewer = "viewer"


class UserTenantRole(Base):
    """Associates a user with a tenant and assigns them a role."""

    __tablename__ = "user_tenant_roles"

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "tenant_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum", create_type=True),
        nullable=False,
    )
