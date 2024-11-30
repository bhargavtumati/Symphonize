"""create_stages_table

Revision ID: d71eb36c726e
Revises: 0f4e44666059
Create Date: 2024-11-14 12:49:09.269592

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd71eb36c726e'
down_revision: Union[str, None] = '0f4e44666059'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'stages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('recruiter_id', sa.Integer, sa.ForeignKey('recruiter.id')),
        sa.Column('job_id', sa.Integer, sa.ForeignKey('job.id')),
        sa.Column('stages', JSONB, nullable=False),
        sa.Column('meta', JSONB, nullable=False)
    )


def downgrade() -> None:
    op.drop_table('stages')
