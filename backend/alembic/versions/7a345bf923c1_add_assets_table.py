"""Add assets table

Revision ID: 7a345bf923c1
Revises: 62e4a0f2f4c9
Create Date: 2026-03-30 08:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7a345bf923c1'
down_revision: Union[str, None] = '62e4a0f2f4c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table
    op.create_table('assets',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('cw_configuration_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('type_name', sa.String(length=100), nullable=True),
    sa.Column('status_name', sa.String(length=100), nullable=True),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_tenant_id'), 'assets', ['tenant_id'], unique=False)

    # Enable RLS
    op.execute("ALTER TABLE assets ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE assets FORCE ROW LEVEL SECURITY")

    # Create tenant isolation policy
    op.execute("""
        CREATE POLICY tenant_isolation ON assets
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    """)

    # Superadmin bypass
    op.execute("""
        CREATE POLICY superadmin_bypass ON assets
        USING (current_setting('app.is_superadmin', true)::boolean = true)
    """)

def downgrade() -> None:
    # Remove RLS policies before dropping table
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON assets")
    op.execute("DROP POLICY IF EXISTS superadmin_bypass ON assets")
    op.execute("ALTER TABLE assets DISABLE ROW LEVEL SECURITY")

    # Drop table
    op.drop_index(op.f('ix_assets_tenant_id'), table_name='assets')
    op.drop_table('assets')
