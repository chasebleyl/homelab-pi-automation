"""Repository pattern for data access."""
import logging
from typing import Optional
from datetime import datetime

from .connection import Database
from .predecessor import ProcessedMatch
from .belica_bot import SubscribedProfile, TargetChannel

logger = logging.getLogger("data.repositories")


class ProcessedMatchRepository:
    """Repository for processed match data."""
    
    def __init__(self, db: Database) -> None:
        """
        Initialize the repository.
        
        Args:
            db: Database connection instance
        """
        self.db = db
    
    async def is_match_processed(self, match_uuid: str) -> bool:
        """Check if a match has already been processed."""
        async with self.db.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM processed_matches WHERE match_uuid = $1)",
                match_uuid
            )
            return bool(result)
    
    async def mark_match_processed(
        self, 
        match_uuid: str, 
        match_id: str, 
        end_time: str | datetime
    ) -> None:
        """
        Mark a match as processed.
        
        Args:
            match_uuid: The match UUID
            match_id: The match ID
            end_time: The match end time (ISO string or datetime)
        """
        # Convert datetime to string if needed
        if isinstance(end_time, datetime):
            end_time = end_time.isoformat()
        
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO processed_matches (match_uuid, match_id, end_time)
                VALUES ($1, $2, $3)
                ON CONFLICT (match_uuid) DO NOTHING
            """, match_uuid, match_id, end_time)
    
    async def mark_match_notified(self, match_uuid: str) -> None:
        """Mark a match as having been notified to the bot."""
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                UPDATE processed_matches
                SET notified_bot = TRUE
                WHERE match_uuid = $1
            """, match_uuid)
    
    async def get_match(self, match_uuid: str) -> Optional[ProcessedMatch]:
        """Get a processed match by UUID."""
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM processed_matches WHERE match_uuid = $1",
                match_uuid
            )
            if row:
                return ProcessedMatch.from_row(dict(row))
            return None
    
    async def get_unnotified_matches(self, limit: Optional[int] = None) -> list[ProcessedMatch]:
        """Get matches that haven't been notified to the bot yet."""
        query = "SELECT * FROM processed_matches WHERE notified_bot = FALSE ORDER BY processed_at ASC"
        if limit:
            query += f" LIMIT {limit}"
        
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [ProcessedMatch.from_row(dict(row)) for row in rows]


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

