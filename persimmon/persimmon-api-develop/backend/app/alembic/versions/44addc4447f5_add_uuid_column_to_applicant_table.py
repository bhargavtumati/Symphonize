"""Add uuid column to applicant table

Revision ID: 44addc4447f5
Revises: 61c114a0a060
Create Date: 2024-11-23 14:43:58.328839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
import uuid


# revision identifiers, used by Alembic.
revision: str = '44addc4447f5'
down_revision: Union[str, None] = '61c114a0a060'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def populate_data():
    connection = op.get_bind()

    applicants = connection.execute( 
        sa.text("SELECT applicant.id, applicant.uuid FROM applicant WHERE applicant.uuid IS NULL ORDER BY applicant.id ASC") 
    ).fetchall()

    for applicant in applicants:
        uid = str(uuid.uuid4())
        connection.execute(
            sa.text("UPDATE applicant SET uuid = :uuid WHERE id = :applicant_id"),
            {'uuid': uid, 'applicant_id': applicant.id}
        )

def upgrade() -> None:
    # Step 1: Add the new column
    op.add_column('applicant', sa.Column('uuid', sa.String(), nullable=True))

    # Step 2: Commit the transaction to ensure column is added
    bind = op.get_bind()
    session = Session(bind=bind)
    session.commit()

    # Step 3: Populate the column with some desired data
    populate_data()

    # Step 4: Alter the column to be NOT NULL and unique
    op.alter_column('applicant', 'uuid', nullable=False, unique=True)


def downgrade() -> None:
    op.drop_column('applicant', 'uuid')