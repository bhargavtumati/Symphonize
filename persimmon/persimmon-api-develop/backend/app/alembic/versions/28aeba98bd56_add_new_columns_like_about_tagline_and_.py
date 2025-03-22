"""add new columns like about tagline and social media links to company table

Revision ID: 28aeba98bd56
Revises: b98ba5b3b61a
Create Date: 2025-03-18 12:39:05.337137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '28aeba98bd56'
down_revision: Union[str, None] = 'b98ba5b3b61a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the business type enum properly
business_type_enum = sa.Enum(
    'B2B', 'B2C', 'C2C', 'C2B', 'B2G', 'G2B', 'G2C', 
    'D2C', 'B2B2C', 'B2B SaaS', 'P2P', 'M2C', 
    name='BusinessType',
    schema='enum'
)

def upgrade() -> None:
    business_type_enum.create(op.get_bind())
    op.add_column('company', sa.Column('tagline', sa.String, nullable=True), schema='public')
    op.add_column('company', sa.Column('business_type', business_type_enum, nullable=True), schema='public')
    op.add_column('company', sa.Column('about', sa.String(length=1000), nullable=True), schema='public')
    op.add_column('company', sa.Column('logo', sa.String, nullable=True), schema='public')
    op.add_column('company', sa.Column('images', JSONB, nullable=True), schema='public')
    op.add_column('company', sa.Column('instagram', sa.String(length=255), nullable=True, unique=True), schema='public')
    op.add_column('company', sa.Column('facebook', sa.String(length=255), nullable=True, unique=True), schema='public')
    op.add_column('company', sa.Column('twitter', sa.String(length=255), nullable=True, unique=True), schema='public')


def downgrade() -> None:
    op.drop_column('company', 'tagline', schema='public')
    op.drop_column('company', 'business_type', schema='public')
    op.drop_column('company', 'about', schema='public')
    op.drop_column('company', 'logo', schema='public')
    op.drop_column('company', 'images', schema='public')
    op.drop_column('company', 'instagram', schema='public')
    op.drop_column('company', 'facebook', schema='public')
    op.drop_column('company', 'twitter', schema='public')

    business_type_enum.drop(op.get_bind())
