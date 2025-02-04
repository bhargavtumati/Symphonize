"""add_index_to_email_id_column_in_the_recruiter_table

Revision ID: 68d6b990575e
Revises: 4dfee85007d2
Create Date: 2024-12-16 08:53:43.078391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68d6b990575e'
down_revision: Union[str, None] = '4dfee85007d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_recruiter_email_id', 'recruiter', ['email_id'])

def downgrade() -> None:
    op.drop_index('ix_recruiter_email_id', table_name='recruiter')
