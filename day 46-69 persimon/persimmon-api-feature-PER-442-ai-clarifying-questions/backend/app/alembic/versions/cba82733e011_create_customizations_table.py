"""Create customizations table

Revision ID: cba82733e011
Revises: 4dfee85007d2
Create Date: 2024-12-19 11:13:06.257270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cba82733e011'
down_revision: Union[str, None] = '4dfee85007d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    

    # Create the `customizations` table with the new schema
    op.create_table(
        'customizations',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('settings', JSONB, nullable=False, server_default='{}'),
        sa.Column('meta', JSONB, nullable=False, server_default='{}'),
    )


def downgrade() -> None:
    # Drop the newly created `customizations` table
    op.drop_table('customizations')

