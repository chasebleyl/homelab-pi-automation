"""Database-backed channel configuration management for guild-specific target channels."""
import logging
from typing import Optional

from data import Database, TargetChannelRepository

logger = logging.getLogger("belica.channel_config")


class ChannelConfig:
    """Manages channel configurations per guild (server) using database."""
    
    def __init__(self, db: Optional[Database] = None) -> None:
        """
        Initialize the channel configuration manager.
        
        Args:
            db: Optional Database instance. If None, creates a new one.
        """
        self.db = db
        self._repo: Optional[TargetChannelRepository] = None
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
            
            self._repo = TargetChannelRepository(self.db)
            self._db_initialized = True
    
    async def add_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Add a channel to the target channels for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to add
            
        Returns:
            True if channel was added, False if it already exists
        """
        await self._ensure_db()
        return await self._repo.add_channel(guild_id, channel_id)
    
    async def remove_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Remove a channel from the target channels for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to remove
            
        Returns:
            True if channel was removed, False if it wasn't configured
        """
        await self._ensure_db()
        return await self._repo.remove_channel(guild_id, channel_id)
    
    async def get_channels(self, guild_id: int) -> list[int]:
        """
        Get all configured target channels for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            
        Returns:
            List of channel IDs, empty list if none configured
        """
        await self._ensure_db()
        return await self._repo.get_channels(guild_id)
    
    async def is_target_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Check if a channel is configured as a target channel for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to check
            
        Returns:
            True if the channel is configured, False otherwise
        """
        await self._ensure_db()
        return await self._repo.is_target_channel(guild_id, channel_id)
    
    async def clear_guild(self, guild_id: int) -> int:
        """
        Clear all target channels for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            
        Returns:
            Number of channels that were removed
        """
        await self._ensure_db()
        return await self._repo.clear_guild(guild_id)
    
    async def get_all_target_channels(self) -> list[tuple[int, int]]:
        """
        Get all target channels across all guilds.
        
        Returns:
            List of (guild_id, channel_id) tuples
        """
        await self._ensure_db()
        return await self._repo.get_all_target_channels()
    
    async def close(self) -> None:
        """Close database connection if we own it."""
        if self.db and self._db_initialized:
            await self.db.close()

