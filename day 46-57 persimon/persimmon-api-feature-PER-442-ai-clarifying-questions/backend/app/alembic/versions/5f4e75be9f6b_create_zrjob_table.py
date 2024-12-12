"""create zrjob table

Revision ID: 5f4e75be9f6b
Revises: 9959c61f4e13
Create Date: 2024-09-27 16:32:39.110402

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f4e75be9f6b'
down_revision: Union[str, None] = '9959c61f4e13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'zrjob',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('detail', JSONB),
        sa.Column('features', JSONB),
        sa.Column('meta', JSONB),
    )


def downgrade() -> None:
    op.drop_table('zrjob')
