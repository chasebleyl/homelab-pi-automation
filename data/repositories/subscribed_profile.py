"""Repository for subscribed player profiles."""
import logging
from typing import Optional

from ..connection import Database
from ..belica_bot import SubscribedProfile

logger = logging.getLogger("data.repositories.subscribed_profile")


class SubscribedProfileRepository:
    """Repository for subscribed player profiles."""

    def __init__(self, db: Database) -> None:
        """
        Initialize the repository.

        Args:
            db: Database connection instance
        """
        self.db = db

    async def add_profile(self, guild_id: int, player_uuid: str) -> bool:
        """
        Add a player profile subscription for a guild.

        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID from pred.gg

        Returns:
            True if profile was added, False if it already exists
        """
        async with self.db.pool.acquire() as conn:
            # Check if already exists
            exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM subscribed_profiles
                    WHERE guild_id = $1 AND player_uuid = $2
                )
            """, guild_id, player_uuid)

            if exists:
                return False

            # Insert the new subscription
            try:
                await conn.execute("""
                    INSERT INTO subscribed_profiles (guild_id, player_uuid, subscribed_at)
                    VALUES ($1, $2, NOW())
                """, guild_id, player_uuid)
                return True
            except Exception as e:
                logger.error(f"Error adding profile subscription: {e}")
                return False

    async def remove_profile(self, guild_id: int, player_uuid: str) -> bool:
        """
        Remove a player profile subscription for a guild.

        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID to remove

        Returns:
            True if profile was removed, False if it wasn't subscribed
        """
        async with self.db.pool.acquire() as conn:
            # Check if exists first, then delete
            exists = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM subscribed_profiles
                    WHERE guild_id = $1 AND player_uuid = $2
                )
            """, guild_id, player_uuid)

            if not exists:
                return False

            await conn.execute("""
                DELETE FROM subscribed_profiles
                WHERE guild_id = $1 AND player_uuid = $2
            """, guild_id, player_uuid)
            return True

    async def get_profiles(self, guild_id: int) -> list[str]:
        """
        Get all subscribed player profiles for a guild.

        Args:
            guild_id: The Discord guild (server) ID

        Returns:
            List of player UUIDs, empty list if none subscribed
        """
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT player_uuid FROM subscribed_profiles
                WHERE guild_id = $1
                ORDER BY subscribed_at ASC
            """, guild_id)
            return [row["player_uuid"] for row in rows]

    async def is_subscribed(self, guild_id: int, player_uuid: str) -> bool:
        """
        Check if a player profile is subscribed for a guild.

        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID to check

        Returns:
            True if the profile is subscribed, False otherwise
        """
        async with self.db.pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM subscribed_profiles
                    WHERE guild_id = $1 AND player_uuid = $2
                )
            """, guild_id, player_uuid)
            return bool(result)

    async def clear_guild(self, guild_id: int) -> int:
        """
        Clear all profile subscriptions for a guild.

        Args:
            guild_id: The Discord guild (server) ID

        Returns:
            Number of profiles that were removed
        """
        async with self.db.pool.acquire() as conn:
            # Get count before deletion
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM subscribed_profiles WHERE guild_id = $1
            """, guild_id)
            # Delete all subscriptions for this guild
            await conn.execute("""
                DELETE FROM subscribed_profiles WHERE guild_id = $1
            """, guild_id)
            return int(count) if count else 0

    async def get_all_subscriptions(self) -> list[SubscribedProfile]:
        """Get all subscribed profiles across all guilds."""
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM subscribed_profiles
                ORDER BY guild_id, subscribed_at ASC
            """)
            return [SubscribedProfile.from_row(dict(row)) for row in rows]

    async def get_subscription(self, guild_id: int, player_uuid: str) -> Optional[SubscribedProfile]:
        """Get a specific subscription."""
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM subscribed_profiles
                WHERE guild_id = $1 AND player_uuid = $2
            """, guild_id, player_uuid)
            if row:
                return SubscribedProfile.from_row(dict(row))
            return None
