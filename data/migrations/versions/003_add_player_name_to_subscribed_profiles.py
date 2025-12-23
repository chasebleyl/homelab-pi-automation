"""Add player_name column to subscribed_profiles table

Revision ID: 003
Revises: 002
Create Date: 2024-12-23
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add player_name column - nullable since existing rows won't have it
    op.execute("""
        ALTER TABLE subscribed_profiles
        ADD COLUMN player_name TEXT
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE subscribed_profiles
        DROP COLUMN player_name
    """)
