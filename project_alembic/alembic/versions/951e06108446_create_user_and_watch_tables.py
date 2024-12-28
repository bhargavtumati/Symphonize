"""Create user and watch tables

Revision ID: 951e06108446
Revises: 5922d0a38b7f
Create Date: 2024-12-13 15:36:38.622417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '951e06108446'
down_revision: Union[str, None] = '5922d0a38b7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, index=True),
        sa.Column('email', sa.String, unique=True, index=True),
        sa.Column('created_at', sa.DateTime, default=func.now())
    )

    op.create_table(
        'watch',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, index=True),
        sa.Column('company', sa.String, unique=True, index=True),
        sa.Column('created_at', sa.DateTime, default=func.now())
    )

def downgrade():
    op.drop_table('users')
    op.drop_table('watch')
