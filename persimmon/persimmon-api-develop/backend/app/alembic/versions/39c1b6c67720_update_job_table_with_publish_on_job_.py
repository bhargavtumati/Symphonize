"""Update Job Table with publish on job boards

Revision ID: 39c1b6c67720
Revises: 8c2e80cd0ee8
Create Date: 2025-04-30 16:34:44.002553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39c1b6c67720'
down_revision: Union[str, None] = '8c2e80cd0ee8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'job',
        sa.Column(
            'published_on_other_domains',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )


def downgrade() -> None:
    op.drop_column('job', 'published_on_other_domains')