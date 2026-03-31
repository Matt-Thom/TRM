"""Update risk asset mapping

Revision ID: 8b456cf034d2
Revises: 7a345bf923c1
Create Date: 2026-03-30 08:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8b456cf034d2'
down_revision: Union[str, None] = '7a345bf923c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add foreign key to asset table. Allowing null for existing risks or custom assets.
    op.add_column('risks', sa.Column('asset_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_risks_asset_id', 'risks', 'assets', ['asset_id'], ['id'])

    # Optional: We could make asset_at_risk nullable if we wanted to fully transition to asset_id
    # But for now, we'll keep it as text fallback.
    op.alter_column('risks', 'asset_at_risk', existing_type=sa.Text(), nullable=True)

def downgrade() -> None:
    op.alter_column('risks', 'asset_at_risk', existing_type=sa.Text(), nullable=False)
    op.drop_constraint('fk_risks_asset_id', 'risks', type_='foreignkey')
    op.drop_column('risks', 'asset_id')
