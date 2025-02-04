"""create candidacy table

Revision ID: 27cfe278e544
Revises: 5f4e75be9f6b
Create Date: 2024-09-27 16:35:25.639338

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27cfe278e544'
down_revision: Union[str, None] = '5f4e75be9f6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'candidacy',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('job_id', sa.Integer, sa.ForeignKey('public.zrjob.id')),
        sa.Column('resume_id', sa.Integer, sa.ForeignKey('public.resume.id')),
        sa.Column('match', JSONB),
        sa.Column('meta', JSONB),
    )


def downgrade() -> None:
    op.drop_table('candidacy')
