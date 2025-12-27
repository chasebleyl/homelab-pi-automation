"""Add composite indexes for query optimization

Revision ID: 004
Revises: 003
Create Date: 2024-12-27

Adds composite indexes to optimize common query patterns:
- subscribed_profiles: (guild_id, subscribed_at) for sorted profile listings
- target_channels: (guild_id, configured_at) for sorted channel listings
- processed_matches: (notified_bot, processed_at) for unnotified match queries
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite index for subscribed_profiles: optimizes get_profiles() and
    # get_profiles_with_names() which filter by guild_id and sort by subscribed_at
    op.execute("""
        CREATE INDEX idx_subscribed_profiles_guild_id_subscribed_at
            ON subscribed_profiles(guild_id, subscribed_at)
    """)

    # Composite index for target_channels: optimizes get_channels() which
    # filters by guild_id and sorts by configured_at
    op.execute("""
        CREATE INDEX idx_target_channels_guild_id_configured_at
            ON target_channels(guild_id, configured_at)
    """)

    # Composite index for processed_matches: optimizes get_unnotified_matches()
    # which filters on notified_bot = FALSE and sorts by processed_at
    op.execute("""
        CREATE INDEX idx_processed_matches_notified_bot_processed_at
            ON processed_matches(notified_bot, processed_at)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_processed_matches_notified_bot_processed_at")
    op.execute("DROP INDEX IF EXISTS idx_target_channels_guild_id_configured_at")
    op.execute("DROP INDEX IF EXISTS idx_subscribed_profiles_guild_id_subscribed_at")
