"""Add player_match_cursors table for per-player cursor tracking

Revision ID: 002
Revises: 001
Create Date: 2024-12-22
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # player_match_cursors - tracks the last fetched match timestamp per player
    op.execute("""
        CREATE TABLE player_match_cursors (
            player_uuid TEXT PRIMARY KEY,
            last_match_end_time TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX idx_player_match_cursors_last_match_end_time
            ON player_match_cursors(last_match_end_time)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS player_match_cursors")
