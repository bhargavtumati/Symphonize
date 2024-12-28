"""create zrapplicant table

Revision ID: a558567aacad
Revises: 
Create Date: 2024-09-11 12:03:37.832154

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a558567aacad'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'zrapplicant',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Unicode(200)),
        sa.Column('candidate_id', sa.String(32)),
        sa.Column('applicant_id', sa.String(32)),
        sa.Column('job_id', sa.String(32)),
        sa.Column('attachments', JSONB),
        sa.Column('detail', JSONB),
        sa.Column('meta', JSONB),
    )


def downgrade() -> None:
    op.drop_table('zrapplicant')