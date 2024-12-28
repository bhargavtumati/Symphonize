"""Add code column to job table

Revision ID: 61c114a0a060
Revises: d71eb36c726e
Create Date: 2024-11-20 17:57:48.660226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision: str = '61c114a0a060'
down_revision: Union[str, None] = 'd71eb36c726e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def get_next_sequence_number(connection, company_code):
    result = connection.execute(
        sa.text("SELECT MAX(CAST(SUBSTRING(code, 4, LENGTH(code) - 3) AS INTEGER)) FROM job WHERE code LIKE :prefix"),
        {'prefix': f"{company_code}%"}
    ).scalar()
    return (result or 0) + 1

def populate_data():
    connection = op.get_bind()

    jobs = connection.execute(
        sa.text(
            """
            SELECT job.id, job.company_id, job.code, company.name AS company_name
            FROM job
            JOIN company ON job.company_id = company.id
            WHERE job.code IS NULL
            ORDER BY job.id ASC
            """
        )
    ).fetchall()
    
    for job in jobs:
        job_id = job.id
        company_name = job.company_name
        company_code = company_name.capitalize()[:3]
        next_sequence_number = get_next_sequence_number(connection, company_code)
        
        job_code = f"{company_code}{next_sequence_number:04d}" 
        connection.execute(
            sa.text("UPDATE job SET code = :job_code WHERE id = :job_id"),
            {'job_code': job_code, 'job_id': job_id}
        )

def upgrade() -> None:
    # Step 1: Add the new column
    op.add_column('job', sa.Column('code', sa.String(), nullable=True))
    
    # Step 2: Commit the transaction to ensure column is added
    bind = op.get_bind()
    session = Session(bind=bind)
    session.commit()
    
    # Step 3: Populate the column with some desired data
    populate_data()
    
    # Step 4: Alter the column to be NOT NULL and unique
    op.alter_column('job', 'code', nullable=False, unique=True)

def downgrade() -> None:
    op.drop_column('job', 'code')


