"""alter the column types of min and max experience from integer to float

Revision ID: 8f5e292d1d71
Revises: e0e89645afed
Create Date: 2025-03-10 15:28:02.636532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f5e292d1d71'
down_revision: Union[str, None] = 'e0e89645afed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("ALTER TABLE job ALTER COLUMN min_experience TYPE FLOAT USING min_experience::FLOAT;")
    op.execute("ALTER TABLE job ALTER COLUMN max_experience TYPE FLOAT USING max_experience::FLOAT;")

def downgrade():
    op.execute("ALTER TABLE job ALTER COLUMN min_experience TYPE INTEGER USING min_experience::INTEGER;")
    op.execute("ALTER TABLE job ALTER COLUMN max_experience TYPE INTEGER USING max_experience::INTEGER;")

