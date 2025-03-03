"""create integration table

Revision ID: 641970544b47
Revises: de7a178041f7
Create Date: 2025-01-30 12:48:18.781894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

# revision identifiers, used by Alembic.
revision: str = '641970544b47'
down_revision: Union[str, None] = 'de7a178041f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'integration',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('credentials', MutableDict.as_mutable(JSONB), nullable=False),
        sa.Column('company_id', sa.Integer, sa.ForeignKey('public.company.id'), nullable=False),
        sa.Column('meta', MutableDict.as_mutable(JSONB), nullable=False),
    )


def downgrade():
    op.drop_table('integration')
