"""insert default designation names to master data table

Revision ID: 41b237edf3ab
Revises: 06b5b560f561
Create Date: 2025-04-08 12:52:00.594305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.models.master_data import MasterData

# revision identifiers, used by Alembic.
revision: str = '41b237edf3ab'
down_revision: Union[str, None] = '06b5b560f561'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    MasterData.insert_default_designations(session=session)


def downgrade() -> None:
    op.execute(
        sa.sql.text("DELETE FROM master_data WHERE type = 'designation'")
    )
