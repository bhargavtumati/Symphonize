"""create master_data table

Revision ID: 52da54b75bd9
Revises: 3e407a21b9be
Create Date: 2024-10-24 14:51:26.347855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB
from app.models.master_data import MasterData

# revision identifiers, used by Alembic.
revision: str = '52da54b75bd9'
down_revision: Union[str, None] = '3e407a21b9be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'master_data',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('value', JSONB, nullable=False),
        sa.Column('type', sa.String, nullable=False)
    )
    #Commit the transaction to ensure table is created
    bind = op.get_bind()
    session = Session(bind=bind)
    session.commit()
    MasterData.seed_master_data(session=session)

def downgrade() -> None:
    op.drop_table('master_data')
