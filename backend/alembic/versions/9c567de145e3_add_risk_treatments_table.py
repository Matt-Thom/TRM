"""Add risk_treatments table

Revision ID: 9c567de145e3
Revises: 8b456cf034d2
Create Date: 2026-03-30 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9c567de145e3'
down_revision: Union[str, None] = '8b456cf034d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table
    op.create_table('risk_treatments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('risk_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('state', sa.String(length=50), nullable=False),
    sa.Column('target_likelihood', sa.Integer(), nullable=False),
    sa.Column('target_impact', sa.Integer(), nullable=False),
    sa.Column('target_residual_score', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=True),
    sa.Column('due_date', sa.String(length=50), nullable=True),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['risk_id'], ['risks.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_treatments_tenant_id'), 'risk_treatments', ['tenant_id'], unique=False)

    # Enable RLS
    op.execute("ALTER TABLE risk_treatments ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE risk_treatments FORCE ROW LEVEL SECURITY")

    # Create tenant isolation policy
    op.execute("""
        CREATE POLICY tenant_isolation ON risk_treatments
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    """)

    # Superadmin bypass
    op.execute("""
        CREATE POLICY superadmin_bypass ON risk_treatments
        USING (current_setting('app.is_superadmin', true)::boolean = true)
    """)

def downgrade() -> None:
    # Remove RLS policies before dropping table
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON risk_treatments")
    op.execute("DROP POLICY IF EXISTS superadmin_bypass ON risk_treatments")
    op.execute("ALTER TABLE risk_treatments DISABLE ROW LEVEL SECURITY")

    # Drop table
    op.drop_index(op.f('ix_risk_treatments_tenant_id'), table_name='risk_treatments')
    op.drop_table('risk_treatments')
