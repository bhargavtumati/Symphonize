"""add enhanced_description column to job table

Revision ID: 4dfee85007d2
Revises: 44addc4447f5
Create Date: 2024-11-23 15:23:33.651170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '4dfee85007d2'
down_revision: Union[str, None] = '44addc4447f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'job',
          sa.Column('enhanced_description',JSONB,nullable=False,server_default=sa.text("'{}'"))
         )

def downgrade() -> None:
    op.drop_column('job', 'enhanced_description')
