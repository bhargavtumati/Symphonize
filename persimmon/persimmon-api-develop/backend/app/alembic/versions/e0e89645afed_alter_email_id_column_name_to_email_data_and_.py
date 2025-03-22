"""alter email_id column name to email_data and type to jsonb

Revision ID: e0e89645afed
Revises: faaa80c82216
Create Date: 2025-03-06 13:19:49.409921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0e89645afed'
down_revision: Union[str, None] = 'faaa80c82216'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('template', 'email_id', new_column_name='email_data', schema='public')

    op.execute("""
        ALTER TABLE public.template
        ALTER COLUMN email_data TYPE JSONB
        USING jsonb_build_object('id', email_data, 'send_count', 0);
    """)


def downgrade():
    op.execute("""
        ALTER TABLE public.template
        ALTER COLUMN email_data TYPE VARCHAR(255)
        USING email_data->>'id';
    """)

    op.alter_column('template', 'email_data', new_column_name='email_id', schema='public')
