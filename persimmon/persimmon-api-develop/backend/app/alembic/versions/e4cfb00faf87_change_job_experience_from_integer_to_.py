"""Change job.experience from Integer to Float

Revision ID: e4cfb00faf87
Revises: faaa80c82216
Create Date: 2025-03-06 17:05:32.311811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4cfb00faf87'
down_revision: Union[str, None] = 'faaa80c82216'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Alter min_experience and max_experience columns from Integer to Float
    with op.batch_alter_table('job') as batch_op:
        batch_op.alter_column('min_experience', type_=sa.Float(), existing_type=sa.Integer())
        batch_op.alter_column('max_experience', type_=sa.Float(), existing_type=sa.Integer())

def downgrade():
    # Revert min_experience and max_experience back to Integer
    with op.batch_alter_table('job') as batch_op:
        batch_op.alter_column('min_experience', type_=sa.Integer(), existing_type=sa.Float())
        batch_op.alter_column('max_experience', type_=sa.Integer(), existing_type=sa.Float())
