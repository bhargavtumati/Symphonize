"""add currency Property to job table

Revision ID: 859821e47a38
Revises: 41b237edf3ab
Create Date: 2025-04-09 18:59:51.701433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '859821e47a38'
down_revision: Union[str, None] = '41b237edf3ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('job', sa.Column("currency", sa.String(length=3), server_default="INR" ,nullable=False), schema='public')


def downgrade() -> None:
    op.drop_column('job', 'currency', schema='public')
