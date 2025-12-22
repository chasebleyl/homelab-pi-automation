"""Channel configuration management for guild-specific target channels."""
import json
import logging
from pathlib import Path
from typing import Optional, Set

logger = logging.getLogger("belica.channel_config")


class ChannelConfig:
    """Manages channel configurations per guild (server)."""
    
    def __init__(self, config_file: str = "channel_config.json") -> None:
        """
        Initialize the channel configuration manager.
        
        Args:
            config_file: Path to the JSON file storing channel configurations
        """
        self.config_file = Path(config_file)
        self._config: dict[int, list[int]] = {}  # guild_id -> list of channel_ids
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert string keys to int (JSON keys are strings)
                    self._config = {int(guild_id): channel_ids for guild_id, channel_ids in data.items()}
                logger.info(f"Loaded channel config for {len(self._config)} guild(s)")
            except (json.JSONDecodeError, ValueError, IOError) as e:
                logger.warning(f"Failed to load channel config: {e}. Starting with empty config.")
                self._config = {}
        else:
            logger.info("No existing channel config file found. Starting with empty config.")
            self._config = {}
    
    def _save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                # Convert int keys to strings for JSON
                data = {str(guild_id): channel_ids for guild_id, channel_ids in self._config.items()}
                json.dump(data, f, indent=2)
            logger.debug(f"Saved channel config for {len(self._config)} guild(s)")
        except IOError as e:
            logger.error(f"Failed to save channel config: {e}")
            raise
    
    def add_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Add a channel to the target channels for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to add
            
        Returns:
            True if channel was added, False if it already exists
        """
        if guild_id not in self._config:
            self._config[guild_id] = []
        
        if channel_id not in self._config[guild_id]:
            self._config[guild_id].append(channel_id)
            self._save()
            logger.info(f"Added channel {channel_id} to guild {guild_id}")
            return True
        else:
            logger.debug(f"Channel {channel_id} already configured for guild {guild_id}")
            return False
    
    def remove_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Remove a channel from the target channels for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to remove
            
        Returns:
            True if channel was removed, False if it wasn't configured
        """
        if guild_id in self._config and channel_id in self._config[guild_id]:
            self._config[guild_id].remove(channel_id)
            # Clean up empty guild entries
            if not self._config[guild_id]:
                del self._config[guild_id]
            self._save()
            logger.info(f"Removed channel {channel_id} from guild {guild_id}")
            return True
        else:
            logger.debug(f"Channel {channel_id} not configured for guild {guild_id}")
            return False
    
    def get_channels(self, guild_id: int) -> list[int]:
        """
        Get all configured target channels for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            
        Returns:
            List of channel IDs, empty list if none configured
        """
        return self._config.get(guild_id, []).copy()
    
    def is_target_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Check if a channel is configured as a target channel for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            channel_id: The Discord channel ID to check
            
        Returns:
            True if the channel is configured, False otherwise
        """
        return guild_id in self._config and channel_id in self._config[guild_id]
    
    def clear_guild(self, guild_id: int) -> int:
        """
        Clear all target channels for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            
        Returns:
            Number of channels that were removed
        """
        count = len(self._config.get(guild_id, []))
        if guild_id in self._config:
            del self._config[guild_id]
            self._save()
            logger.info(f"Cleared {count} channel(s) for guild {guild_id}")
        return count
    
    def get_all_target_channels(self) -> list[tuple[int, int]]:
        """
        Get all target channels across all guilds.
        
        Returns:
            List of (guild_id, channel_id) tuples
        """
        channels = []
        for guild_id, channel_ids in self._config.items():
            for channel_id in channel_ids:
                channels.append((guild_id, channel_id))
        return channels

