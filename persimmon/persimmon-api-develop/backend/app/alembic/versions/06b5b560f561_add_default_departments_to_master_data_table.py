"""add_default_departments_to_master_data_table

Revision ID: 06b5b560f561
Revises: 8096e9f1a36e
Create Date: 2025-04-07 17:30:20.637047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.models.master_data import MasterData


# revision identifiers, used by Alembic.
revision: str = '06b5b560f561'
down_revision: Union[str, None] = '8096e9f1a36e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    session.commit()
    MasterData.add_default_department_names(session=session)


def downgrade() -> None:
    op.execute(
        sa.sql.text("DELETE FROM master_data WHERE type = 'department'")
    )
