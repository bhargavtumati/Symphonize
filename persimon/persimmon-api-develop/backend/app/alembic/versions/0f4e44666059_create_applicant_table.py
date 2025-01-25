"""Create applicant table

Revision ID: 0f4e44666059
Revises: 52da54b75bd9
Create Date: 2024-10-29 14:22:16.900781

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f4e44666059'
down_revision: Union[str, None] = '52da54b75bd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'applicant',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('details', JSONB, nullable=False),
        sa.Column('stage_uuid', sa.String, nullable=False),
        sa.Column('job_id',sa.Integer, sa.ForeignKey('public.job.id')),
        sa.Column('meta', JSONB ,nullable=False )
    )

def downgrade() -> None:
    op.drop_table('applicant')
