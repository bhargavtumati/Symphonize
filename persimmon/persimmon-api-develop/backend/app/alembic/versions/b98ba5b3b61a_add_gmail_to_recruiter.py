"""add-gmail to recruiter

Revision ID: b98ba5b3b61a
Revises: 3039e05d1fa6
Create Date: 2025-03-14 14:29:35.110626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b98ba5b3b61a'
down_revision: Union[str, None] = '3039e05d1fa6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "recruiter",
        sa.Column("gmail_id", sa.String(255), nullable=True,unique=True),
        schema="public",
    )


def downgrade() -> None:
    op.drop_column("recruiter","gmail_id", schema="public")
