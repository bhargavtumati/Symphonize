"""insert default job titles into master data table

Revision ID: 8c2e80cd0ee8
Revises: 859821e47a38
Create Date: 2025-04-15 13:23:04.461870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.master_data import MasterData


# revision identifiers, used by Alembic.
revision: str = '8c2e80cd0ee8'
down_revision: Union[str, None] = '859821e47a38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    MasterData.insert_default_job_titles(session=session)


def downgrade() -> None:
    op.execute(
        sa.sql.text("DELETE FROM master_data WHERE type = 'job title'")
    )
