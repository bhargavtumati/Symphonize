"""create resume table

Revision ID: 9959c61f4e13
Revises: a558567aacad
Create Date: 2024-09-11 12:06:08.247762

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9959c61f4e13'
down_revision: Union[str, None] = 'a558567aacad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'resume',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('detail', JSONB),
        sa.Column('features', JSONB),
        sa.Column('meta', JSONB),
    )


def downgrade() -> None:
    op.drop_table('resume')
