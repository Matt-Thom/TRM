"""Add risk_matrix_config table

Revision ID: 005
Revises: 004
Create Date: 2026-03-30 13:58:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('risk_matrix_config',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('likelihood_labels', postgresql.JSONB(astext_type=sa.Text()), server_default='["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"]', nullable=False),
    sa.Column('impact_labels', postgresql.JSONB(astext_type=sa.Text()), server_default='["Negligible", "Minor", "Moderate", "Major", "Severe"]', nullable=False),
    sa.Column('thresholds', postgresql.JSONB(astext_type=sa.Text()), server_default='{"Low": {"max": 4, "min": 1}, "Medium": {"max": 9, "min": 5}, "High": {"max": 16, "min": 10}, "Critical": {"max": 25, "min": 17}}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_matrix_config_tenant_id'), 'risk_matrix_config', ['tenant_id'], unique=False)

    op.execute("ALTER TABLE risk_matrix_config ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE risk_matrix_config FORCE ROW LEVEL SECURITY")

    op.execute("""
        CREATE POLICY tenant_isolation ON risk_matrix_config
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    """)

    op.execute("""
        CREATE POLICY superadmin_bypass ON risk_matrix_config
        USING (current_setting('app.is_superadmin', true)::boolean = true)
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON risk_matrix_config")
    op.execute("DROP POLICY IF EXISTS superadmin_bypass ON risk_matrix_config")
    op.execute("ALTER TABLE risk_matrix_config DISABLE ROW LEVEL SECURITY")
    op.drop_index(op.f('ix_risk_matrix_config_tenant_id'), table_name='risk_matrix_config')
    op.drop_table('risk_matrix_config')
