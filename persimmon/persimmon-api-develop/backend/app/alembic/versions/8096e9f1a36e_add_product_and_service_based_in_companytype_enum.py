"""Add PRODUCT_AND_SERVICE_BASED to CompanyType enum

Revision ID: 8096e9f1a36e
Revises: 28aeba98bd56
Create Date: 2025-04-03 15:56:15.352264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '8096e9f1a36e'
down_revision: Union[str, None] = '28aeba98bd56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the new ENUM value to the existing type
    op.execute("ALTER TYPE enum.\"CompanyType\" ADD VALUE 'PRODUCT_AND_SERVICE_BASED'")


def downgrade() -> None:
    pass