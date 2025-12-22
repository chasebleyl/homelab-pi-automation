"""Initial schema - processed_matches, subscribed_profiles, target_channels

Revision ID: 001
Revises:
Create Date: 2024-12-22
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # processed_matches - tracks which matches have been fetched from pred.gg API
    op.execute("""
        CREATE TABLE processed_matches (
            match_uuid TEXT PRIMARY KEY,
            match_id TEXT NOT NULL,
            end_time TIMESTAMP WITH TIME ZONE NOT NULL,
            processed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            notified_bot BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    op.execute("""
        CREATE INDEX idx_processed_matches_end_time
            ON processed_matches(end_time)
    """)
    op.execute("""
        CREATE INDEX idx_processed_matches_processed_at
            ON processed_matches(processed_at)
    """)

    # subscribed_profiles - Discord guild subscriptions to player profiles
    op.execute("""
        CREATE TABLE subscribed_profiles (
            guild_id BIGINT NOT NULL,
            player_uuid TEXT NOT NULL,
            subscribed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            PRIMARY KEY (guild_id, player_uuid)
        )
    """)
    op.execute("""
        CREATE INDEX idx_subscribed_profiles_guild_id
            ON subscribed_profiles(guild_id)
    """)
    op.execute("""
        CREATE INDEX idx_subscribed_profiles_player_uuid
            ON subscribed_profiles(player_uuid)
    """)

    # target_channels - Discord channels configured to receive match notifications
    op.execute("""
        CREATE TABLE target_channels (
            guild_id BIGINT NOT NULL,
            channel_id BIGINT NOT NULL,
            configured_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            PRIMARY KEY (guild_id, channel_id)
        )
    """)
    op.execute("""
        CREATE INDEX idx_target_channels_guild_id
            ON target_channels(guild_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS target_channels")
    op.execute("DROP TABLE IF EXISTS subscribed_profiles")
    op.execute("DROP TABLE IF EXISTS processed_matches")
