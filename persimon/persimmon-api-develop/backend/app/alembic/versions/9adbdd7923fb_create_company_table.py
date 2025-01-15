"""create company table

Revision ID: 9adbdd7923fb
Revises: 27cfe278e544
Create Date: 2024-10-24 14:28:41.793702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9adbdd7923fb'
down_revision: Union[str, None] = '27cfe278e544'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS enum')

    op.create_table(
        'company',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=2048), nullable=False),
        sa.Column('number_of_employees', sa.String(length=50), nullable=False),
        sa.Column('industry_type', sa.String(length=255), nullable=False),
        sa.Column('linkedin', sa.String(length=2048), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False, unique=True),
        sa.Column('type', sa.Enum('SERVICE_BASED', 'PRODUCT_BASED', name='CompanyType', schema='enum'), nullable=False),
        sa.Column('meta', postgresql.JSONB, nullable=True)
    )

    # Create an index on the domain column
    op.create_index('ix_company_domain', 'company', ['domain'])


def downgrade() -> None:
    op.drop_index('ix_company_domain', table_name='company')
    op.drop_table('company')
    op.execute('DROP TYPE enum."CompanyType"')
    op.execute('DROP SCHEMA IF EXISTS enum')
