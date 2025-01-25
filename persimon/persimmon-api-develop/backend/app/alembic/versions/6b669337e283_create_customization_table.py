"""create customization table

Revision ID: 6b669337e283
Revises: e22f492e10ac
Create Date: 2024-12-30 08:46:15.633246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict


# revision identifiers, used by Alembic.
revision: str = '6b669337e283'
down_revision: Union[str, None] = 'e22f492e10ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'customization',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('company_id', sa.Integer, sa.ForeignKey('public.company.id'), nullable=False),
        sa.Column('settings', MutableDict.as_mutable(JSONB), nullable=False),
        sa.Column('meta', MutableDict.as_mutable(JSONB), nullable=False),
    )


def downgrade():
    op.drop_table('customization')