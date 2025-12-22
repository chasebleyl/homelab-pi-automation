"""Database-backed profile subscription management for guild-specific player tracking."""
import logging
from typing import Optional

from data import Database, SubscribedProfileRepository

logger = logging.getLogger("belica.profile_subscription")


class ProfileSubscription:
    """Manages player profile subscriptions per guild (server) using database."""
    
    def __init__(self, db: Optional[Database] = None) -> None:
        """
        Initialize the profile subscription manager.
        
        Args:
            db: Optional Database instance. If None, creates a new one.
        """
        self.db = db
        self._repo: Optional[SubscribedProfileRepository] = None
        self._db_initialized = False
    
    async def _ensure_db(self) -> None:
        """Ensure database is connected and repository is initialized."""
        if not self._db_initialized:
            if self.db is None:
                from data import Database
                self.db = Database()
                await self.db.connect()
            elif not self.db._pool:
                await self.db.connect()
            
            self._repo = SubscribedProfileRepository(self.db)
            self._db_initialized = True
    
    async def add_profile(self, guild_id: int, player_uuid: str) -> bool:
        """
        Add a player profile to subscriptions for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID from pred.gg
            
        Returns:
            True if profile was added, False if it already exists
        """
        await self._ensure_db()
        return await self._repo.add_profile(guild_id, player_uuid)
    
    async def remove_profile(self, guild_id: int, player_uuid: str) -> bool:
        """
        Remove a player profile from subscriptions for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID to remove
            
        Returns:
            True if profile was removed, False if it wasn't subscribed
        """
        await self._ensure_db()
        return await self._repo.remove_profile(guild_id, player_uuid)
    
    async def get_profiles(self, guild_id: int) -> list[str]:
        """
        Get all subscribed player profiles for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            
        Returns:
            List of player UUIDs, empty list if none subscribed
        """
        await self._ensure_db()
        return await self._repo.get_profiles(guild_id)
    
    async def is_subscribed(self, guild_id: int, player_uuid: str) -> bool:
        """
        Check if a player profile is subscribed for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID to check
            
        Returns:
            True if the profile is subscribed, False otherwise
        """
        await self._ensure_db()
        return await self._repo.is_subscribed(guild_id, player_uuid)
    
    async def clear_guild(self, guild_id: int) -> int:
        """
        Clear all profile subscriptions for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            
        Returns:
            Number of profiles that were removed
        """
        await self._ensure_db()
        return await self._repo.clear_guild(guild_id)
    
    async def close(self) -> None:
        """Close database connection if we own it."""
        if self.db and self._db_initialized:
            await self.db.close()

