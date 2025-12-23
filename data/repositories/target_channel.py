"""Repository for target channel configurations."""
import logging

from ..connection import Database

logger = logging.getLogger("data.repositories.target_channel")


class TargetChannelRepository:
    """Repository for target channel configurations."""

    def __init__(self, db: Database) -> None:
        """
        Initialize the repository.

        Args:
            db: Database connection instance
        """
        self.db = db

    async def add_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Add a target channel for a guild.

        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to add

        Returns:
            True if channel was added, False if it already exists
        """
        async with self.db.pool.acquire() as conn:
            # Check if already exists
            exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM target_channels
                    WHERE guild_id = $1 AND channel_id = $2
                )
            """, guild_id, channel_id)

            if exists:
                return False

            # Insert the new channel
            try:
                await conn.execute("""
                    INSERT INTO target_channels (guild_id, channel_id, configured_at)
                    VALUES ($1, $2, NOW())
                """, guild_id, channel_id)
                return True
            except Exception as e:
                logger.error(f"Error adding target channel: {e}")
                return False

    async def remove_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Remove a target channel for a guild.

        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to remove

        Returns:
            True if channel was removed, False if it wasn't configured
        """
        async with self.db.pool.acquire() as conn:
            # Check if exists first
            exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM target_channels
                    WHERE guild_id = $1 AND channel_id = $2
                )
            """, guild_id, channel_id)

            if not exists:
                return False

            await conn.execute("""
                DELETE FROM target_channels
                WHERE guild_id = $1 AND channel_id = $2
            """, guild_id, channel_id)
            return True

    async def get_channels(self, guild_id: int) -> list[int]:
        """
        Get all target channels for a guild.

        Args:
            guild_id: The Discord guild (server) ID

        Returns:
            List of channel IDs, empty list if none configured
        """
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT channel_id FROM target_channels
                WHERE guild_id = $1
                ORDER BY configured_at ASC
            """, guild_id)
            return [row["channel_id"] for row in rows]

    async def is_target_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Check if a channel is configured as a target channel for a guild.

        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to check

        Returns:
            True if the channel is configured, False otherwise
        """
        async with self.db.pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM target_channels
                    WHERE guild_id = $1 AND channel_id = $2
                )
            """, guild_id, channel_id)
            return bool(result)

    async def clear_guild(self, guild_id: int) -> int:
        """
        Clear all target channels for a guild.

        Args:
            guild_id: The Discord guild (server) ID

        Returns:
            Number of channels that were removed
        """
        async with self.db.pool.acquire() as conn:
            # Get count before deletion
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM target_channels WHERE guild_id = $1
            """, guild_id)
            # Delete all channels for this guild
            await conn.execute("""
                DELETE FROM target_channels WHERE guild_id = $1
            """, guild_id)
            return int(count) if count else 0

    async def get_all_target_channels(self) -> list[tuple[int, int]]:
        """
        Get all target channels across all guilds.

        Returns:
            List of (guild_id, channel_id) tuples
        """
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT guild_id, channel_id FROM target_channels
                ORDER BY guild_id, configured_at ASC
            """)
            return [(row["guild_id"], row["channel_id"]) for row in rows]
