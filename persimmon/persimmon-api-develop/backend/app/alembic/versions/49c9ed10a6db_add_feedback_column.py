"""add feedback column

Revision ID: 49c9ed10a6db
Revises: 641970544b47
Create Date: 2025-02-27 18:28:40.866178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '49c9ed10a6db'
down_revision: Union[str, None] = '641970544b47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('applicant', sa.Column('feedback', JSONB, nullable=True), schema='public')


def downgrade() -> None:
    op.drop_column('applicant', 'feedback', schema='public')
