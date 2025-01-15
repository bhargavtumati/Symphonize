"""add status column to applicant table

Revision ID: e22f492e10ac
Revises: 68d6b990575e
Create Date: 2024-12-16 16:24:15.912453

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = 'e22f492e10ac'
down_revision: Union[str, None] = '68d6b990575e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('applicant',  sa.Column('status', JSONB, nullable=True),)


def downgrade() -> None:
     op.drop_column('applicant', 'status')
