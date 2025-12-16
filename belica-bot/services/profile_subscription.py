"""Profile subscription management for guild-specific player tracking."""
import json
import logging
from pathlib import Path
from typing import Optional, Set

logger = logging.getLogger("belica.profile_subscription")


class ProfileSubscription:
    """Manages player profile subscriptions per guild (server)."""
    
    def __init__(self, config_file: str = "profile_subscriptions.json") -> None:
        """
        Initialize the profile subscription manager.
        
        Args:
            config_file: Path to the JSON file storing profile subscriptions
        """
        self.config_file = Path(config_file)
        self._config: dict[int, list[str]] = {}  # guild_id -> list of player_uuids
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert string keys to int (JSON keys are strings)
                    self._config = {int(guild_id): player_uuids for guild_id, player_uuids in data.items()}
                logger.info(f"Loaded profile subscriptions for {len(self._config)} guild(s)")
            except (json.JSONDecodeError, ValueError, IOError) as e:
                logger.warning(f"Failed to load profile subscriptions: {e}. Starting with empty config.")
                self._config = {}
        else:
            logger.info("No existing profile subscription file found. Starting with empty config.")
            self._config = {}
    
    def _save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                # Convert int keys to strings for JSON
                data = {str(guild_id): player_uuids for guild_id, player_uuids in self._config.items()}
                json.dump(data, f, indent=2)
            logger.debug(f"Saved profile subscriptions for {len(self._config)} guild(s)")
        except IOError as e:
            logger.error(f"Failed to save profile subscriptions: {e}")
            raise
    
    def add_profile(self, guild_id: int, player_uuid: str) -> bool:
        """
        Add a player profile to subscriptions for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID from pred.gg
            
        Returns:
            True if profile was added, False if it already exists
        """
        if guild_id not in self._config:
            self._config[guild_id] = []
        
        if player_uuid not in self._config[guild_id]:
            self._config[guild_id].append(player_uuid)
            self._save()
            logger.info(f"Added profile {player_uuid} to guild {guild_id}")
            return True
        else:
            logger.debug(f"Profile {player_uuid} already subscribed for guild {guild_id}")
            return False
    
    def remove_profile(self, guild_id: int, player_uuid: str) -> bool:
        """
        Remove a player profile from subscriptions for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID to remove
            
        Returns:
            True if profile was removed, False if it wasn't subscribed
        """
        if guild_id in self._config and player_uuid in self._config[guild_id]:
            self._config[guild_id].remove(player_uuid)
            # Clean up empty guild entries
            if not self._config[guild_id]:
                del self._config[guild_id]
            self._save()
            logger.info(f"Removed profile {player_uuid} from guild {guild_id}")
            return True
        else:
            logger.debug(f"Profile {player_uuid} not subscribed for guild {guild_id}")
            return False
    
    def get_profiles(self, guild_id: int) -> list[str]:
        """
        Get all subscribed player profiles for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            
        Returns:
            List of player UUIDs, empty list if none subscribed
        """
        return self._config.get(guild_id, []).copy()
    
    def is_subscribed(self, guild_id: int, player_uuid: str) -> bool:
        """
        Check if a player profile is subscribed for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            player_uuid: The player UUID to check
            
        Returns:
            True if the profile is subscribed, False otherwise
        """
        return guild_id in self._config and player_uuid in self._config[guild_id]
    
    def clear_guild(self, guild_id: int) -> int:
        """
        Clear all profile subscriptions for a guild.
        
        Args:
            guild_id: The Discord guild (server) ID
            
        Returns:
            Number of profiles that were removed
        """
        count = len(self._config.get(guild_id, []))
        if guild_id in self._config:
            del self._config[guild_id]
            self._save()
            logger.info(f"Cleared {count} profile subscription(s) for guild {guild_id}")
        return count

