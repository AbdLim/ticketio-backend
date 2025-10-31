"""update NFT fdown_revision: Union[str, None] = 'a1737e646ef1'  # Point to the latest migrationelds for Web3

Revision ID: 2025_09_17_update_nft
Revises: 5e151d27666a
Create Date: 2025-09-17 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2025_09_17_update_nft"
down_revision: Union[str, None] = "afab16fce353"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update events table
    op.add_column("events", sa.Column("contract_address", sa.String(), nullable=True))
    op.add_column("events", sa.Column("metadata_uri", sa.String(), nullable=True))
    op.create_index(
        op.f("ix_events_contract_address"), "events", ["contract_address"], unique=True
    )

    # Remove old token_id column from events
    op.drop_column("events", "token_id")

    # Update tickets table
    op.add_column("tickets", sa.Column("token_id", sa.String(), nullable=True))
    op.add_column("tickets", sa.Column("contract_address", sa.String(), nullable=True))
    op.create_index(op.f("ix_tickets_token_id"), "tickets", ["token_id"], unique=True)
    op.create_index(
        op.f("ix_tickets_contract_address"),
        "tickets",
        ["contract_address"],
        unique=False,
    )

    # Remove old serial_number column from tickets
    op.drop_column("tickets", "serial_number")


def downgrade() -> None:
    # Revert tickets table changes
    op.drop_index(op.f("ix_tickets_contract_address"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_token_id"), table_name="tickets")
    op.drop_column("tickets", "contract_address")
    op.drop_column("tickets", "token_id")
    op.add_column("tickets", sa.Column("serial_number", sa.String(), nullable=True))

    # Revert events table changes
    op.drop_index(op.f("ix_events_contract_address"), table_name="events")
    op.drop_column("events", "metadata_uri")
    op.drop_column("events", "contract_address")
    op.add_column("events", sa.Column("token_id", sa.String(), nullable=True))
