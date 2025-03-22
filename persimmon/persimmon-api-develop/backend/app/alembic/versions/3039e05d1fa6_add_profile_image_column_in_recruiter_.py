"""add_profile_image_column_in_recruiter_table

Revision ID: 3039e05d1fa6
Revises: 8f5e292d1d71
Create Date: 2025-03-11 12:34:52.565743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3039e05d1fa6'
down_revision: Union[str, None] = '8f5e292d1d71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "recruiter",
        sa.Column("profile_image", sa.String, nullable=True),
        schema="public",
    )


def downgrade() -> None:
    op.drop_column("recruiter", "profile_image", schema="public")
