"""create_shared_table

Revision ID: faaa80c82216
Revises: 49c9ed10a6db
Create Date: 2025-03-03 13:25:34.649398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'faaa80c82216'
down_revision: Union[str, None] = '49c9ed10a6db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'shared',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('uuid', sa.String, nullable=False, unique=True),
        sa.Column('details', JSONB, nullable=False),
        sa.Column('meta', JSONB, nullable=False)
    )


def downgrade() -> None:
    op.drop_table('shared')
