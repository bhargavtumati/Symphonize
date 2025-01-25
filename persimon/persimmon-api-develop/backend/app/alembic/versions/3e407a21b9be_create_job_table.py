"""create job table

Revision ID: 3e407a21b9be
Revises: dfce47d8fc1d
Create Date: 2024-10-24 14:48:50.630576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '3e407a21b9be'
down_revision: Union[str, None] = 'dfce47d8fc1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'job',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('type', sa.Enum('FULL_TIME', 'PART_TIME', 'FREELANCE', 'CONTRACT', 'INTERNSHIP', name='JobType', schema='enum'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'CLOSED', name='JobStatusType', schema='enum'), default='ACTIVE'),
        sa.Column('workplace_type', sa.Enum('ON_SITE', 'HYBRID', 'REMOTE', name='WorkplaceType', schema='enum'), nullable=False),
        sa.Column('location', sa.String, nullable=False),
        sa.Column('team_size', sa.String, nullable=False),
        sa.Column('min_salary', sa.Float, nullable=False),
        sa.Column('max_salary', sa.Float, nullable=False),
        sa.Column('min_experience', sa.Integer, nullable=False),
        sa.Column('max_experience', sa.Integer, nullable=False),
        sa.Column('target_date', sa.DateTime, nullable=False),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('is_posted_for_client', sa.Boolean, default=False),
        sa.Column('company_id', sa.Integer, sa.ForeignKey('public.company.id')),
        sa.Column('ai_clarifying_questions', JSONB, default=[]),
        sa.Column('publish_on_career_page', sa.Boolean, default=True),
        sa.Column('publish_on_job_boards', JSONB, default=[]),
        sa.Column('meta', JSONB)
    )


def downgrade() -> None:
    op.drop_table('job')

    op.execute('DROP TYPE enum."JobType"')
    op.execute('DROP TYPE enum."JobStatusType"')
    op.execute('DROP TYPE enum."WorkplaceType"')
