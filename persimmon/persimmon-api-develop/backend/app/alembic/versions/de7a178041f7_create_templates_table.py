"""Create templates table

Revision ID: de7a178041f7
Revises: 6b669337e283
Create Date: 2025-01-22 14:46:31.599764

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op
import sqlalchemy as sa
from app.models.template import Template
from app.models.company import Company
from sqlalchemy.orm import Session
import app.helpers.email_helper as emailh



# revision identifiers, used by Alembic.
revision: str = 'de7a178041f7'
down_revision: Union[str, None] = '6b669337e283'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'template',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('company_id', sa.Integer, sa.ForeignKey('company.id')),
        sa.Column('template_data', JSONB, nullable=False),
        sa.Column('email_id', sa.String, nullable=False),
        sa.Column('meta', JSONB, nullable=False),
        schema='public'
    )
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        # Fetch all company records
        company_records = session.query(Company.id).all()
        email_id = "careers@tekworks.ai"  # Replace this with actual logic if needed
        created_by = "pravalika.gulla@tekworks.in"  # Change as required

        # Insert email templates for each company
        for company_record in company_records:
            email_template = Template(
                company_id=company_record.id,
                template_data=emailh.get_email_templates(),
                email_id=email_id
            )
            email_template.create(session=session, created_by=created_by)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def downgrade() -> None:
    op.drop_table('template', schema='public')
