"""create recruiter table

Revision ID: dfce47d8fc1d
Revises: 9adbdd7923fb
Create Date: 2024-10-24 14:46:20.821011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'dfce47d8fc1d'
down_revision: Union[str, None] = '9adbdd7923fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'recruiter',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('whatsapp_number', sa.String(length=20), nullable=False),
        sa.Column('designation', sa.String(length=255), nullable=False),
        sa.Column('linkedin_url', sa.String(length=2048), nullable=False),
        sa.Column('company_id', sa.Integer, sa.ForeignKey('company.id'), nullable=False),
        sa.Column('email_id', sa.String(length=255), nullable=False, unique=True),
        sa.Column('meta', postgresql.JSONB, nullable=True)
    )


def downgrade() -> None:
    op.drop_table('recruiter')
