"""Convert datetime columns to timezone aware

Revision ID: 40c02be18f50
Revises: dc245be159b0
Create Date: 2025-09-18 11:53:44.673648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40c02be18f50'
down_revision: Union[str, Sequence[str], None] = 'dc245be159b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Convert datetime columns to timezone aware
    op.execute("ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE events ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE events ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE events ALTER COLUMN date TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE tickets ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE tickets ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE")


def downgrade() -> None:
    """Downgrade schema."""
    # Convert datetime columns back to timezone naive
    op.execute("ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE events ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE events ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE events ALTER COLUMN date TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE tickets ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE tickets ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE")
