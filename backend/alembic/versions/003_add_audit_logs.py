"""Add audit_logs table with RLS and append-only protection."""

revision = "003"
down_revision = "002"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


def upgrade():
    # Create audit action enum
    op.execute("CREATE TYPE audit_action_enum AS ENUM ('INSERT', 'UPDATE', 'DELETE')")

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("table_name", sa.String(255), nullable=False, index=True),
        sa.Column("record_id", sa.String(255), nullable=False),
        sa.Column("action", sa.Enum("INSERT", "UPDATE", "DELETE", name="audit_action_enum", create_type=False), nullable=False),
        sa.Column("old_values", JSONB, nullable=True),
        sa.Column("new_values", JSONB, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column("request_id", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
    )

    # Enable RLS
    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_logs FORCE ROW LEVEL SECURITY")

    # Tenant isolation policy
    op.execute("""
        CREATE POLICY tenant_isolation ON audit_logs
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    """)

    # Superadmin bypass
    op.execute("""
        CREATE POLICY superadmin_bypass ON audit_logs
        USING (current_setting('app.is_superadmin', true)::boolean = true)
    """)

    # Append-only protection: prevent UPDATE and DELETE on audit_logs
    op.execute("""
        CREATE RULE audit_logs_no_update AS ON UPDATE TO audit_logs
        DO INSTEAD NOTHING
    """)
    op.execute("""
        CREATE RULE audit_logs_no_delete AS ON DELETE TO audit_logs
        DO INSTEAD NOTHING
    """)


def downgrade():
    op.execute("DROP RULE IF EXISTS audit_logs_no_delete ON audit_logs")
    op.execute("DROP RULE IF EXISTS audit_logs_no_update ON audit_logs")
    op.execute("DROP POLICY IF EXISTS superadmin_bypass ON audit_logs")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON audit_logs")
    op.execute("ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY")
    op.drop_table("audit_logs")
    op.execute("DROP TYPE IF EXISTS audit_action_enum")
