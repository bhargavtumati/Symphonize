"""update company table

Revision ID: d67d941dad23
Revises: e4cfb00faf87
Create Date: 2025-03-10 18:22:06.544436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = 'd67d941dad23'
down_revision: Union[str, None] = 'e4cfb00faf87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



# Define the business type enum properly
business_type_enum = sa.Enum(
    'B2B', 'B2C', 'C2C', 'C2B', 'B2G', 'G2B', 'G2C', 
    'D2C', 'B2B2C', 'B2B SaaS', 'P2P', 'M2C', 
    name='BusinessType'
)

def upgrade():
    # Create ENUM type using Alembic rather than raw SQL
    business_type_enum.create(op.get_bind())

    # Rename columns
    op.alter_column('company', 'linkedin', new_column_name='linkedin_url', schema='public')
    op.alter_column('company', 'type', new_column_name='company_type', schema='public')

    # Add new columns
    op.add_column('company', sa.Column('tagline', sa.String(length=255), nullable=True), schema='public')
    op.add_column('company', sa.Column('business_type', business_type_enum, nullable=True), schema='public')
    op.add_column('company', sa.Column('about', sa.String(length=1000), nullable=True), schema='public')
    op.add_column('company', sa.Column('logo', sa.LargeBinary, nullable=True), schema='public')
    op.add_column('company', sa.Column('company_images', sa.ARRAY(sa.LargeBinary), nullable=True), schema='public')
    op.add_column('company', sa.Column('instagram_url', sa.String(length=2048), nullable=True), schema='public')
    op.add_column('company', sa.Column('facebook_url', sa.String(length=2048), nullable=True), schema='public')
    op.add_column('company', sa.Column('x_url', sa.String(length=2048), nullable=True), schema='public')

def downgrade():
    # Drop added columns
    op.drop_column('company', 'tagline', schema='public')
    op.drop_column('company', 'business_type', schema='public')
    op.drop_column('company', 'about', schema='public')
    op.drop_column('company', 'logo', schema='public')
    op.drop_column('company', 'company_images', schema='public')
    op.drop_column('company', 'instagram_url', schema='public')
    op.drop_column('company', 'facebook_url', schema='public')
    op.drop_column('company', 'x_url', schema='public')

    # Rename columns back to original
    op.alter_column('company', 'linkedin_url', new_column_name='linkedin', schema='public')
    op.alter_column('company', 'company_type', new_column_name='type', schema='public')

    # Drop ENUM only if it's not used in any other table
    business_type_enum.drop(op.get_bind())

