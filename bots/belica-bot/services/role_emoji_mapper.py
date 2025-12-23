"""Service for mapping role names to Discord emojis."""
import logging
from typing import Optional
import discord
from discord import utils

logger = logging.getLogger("belica.role_emoji")


class RoleEmojiMapper:
    """Maps role names to Discord emoji references."""

    # Mapping from Role enum values to emoji names (as they appear in Discord)
    ROLE_TO_EMOJI_NAME = {
        "carry": "carry",
        "support": "support",
        "midlane": "midlane",
        "jungle": "jungle",
        "offlane": "offlane",
    }

    def __init__(self, guild: Optional[discord.Guild] = None, bot: Optional[discord.Client] = None):
        """
        Initialize the role emoji mapper.

        Args:
            guild: Optional Discord guild (not used for emoji lookup, kept for compatibility).
            bot: Discord bot client to look up application emojis from.
                 Application emojis are bot-specific and work across all servers.
        """
        self.guild = guild
        self.bot = bot

    def _get_emoji_by_name(self, emoji_name: str) -> Optional[discord.Emoji]:
        """
        Get an emoji by name from bot.emojis or application emojis using discord.utils.get().

        Args:
            emoji_name: The emoji name to search for

        Returns:
            The Emoji object if found, None otherwise
        """
        if not self.bot:
            return None

        # First, check application emojis (bot-specific, work across all servers)
        if hasattr(self.bot, 'application_emojis') and self.bot.application_emojis:
            app_emoji = utils.get(self.bot.application_emojis, name=emoji_name)
            if app_emoji:
                return app_emoji

        # Then, check guild emojis (from all servers the bot is in)
        guild_emoji = utils.get(self.bot.emojis, name=emoji_name)
        return guild_emoji

    def get_emoji_string(self, role_value: str) -> Optional[str]:
        """
        Get the emoji string for a role value.

        Args:
            role_value: Role value from Role enum (e.g., "carry", "support")

        Returns:
            Emoji string in format <:name:id> or <a:name:id>, or None if not found
        """
        emoji_name = self.ROLE_TO_EMOJI_NAME.get(role_value.lower())
        if not emoji_name:
            logger.debug(f"No emoji mapping for role '{role_value}'")
            return None

        emoji = self._get_emoji_by_name(emoji_name)
        if emoji:
            emoji_str = str(emoji)
            logger.debug(f"Found emoji for role '{role_value}': {emoji_str}")
            return emoji_str

        # Try case-insensitive search if exact match failed
        if self.bot:
            for bot_emoji in self.bot.emojis:
                if bot_emoji.name.lower() == emoji_name.lower():
                    emoji_str = str(bot_emoji)
                    logger.debug(f"Found emoji for role '{role_value}' (case-insensitive): {emoji_str}")
                    return emoji_str

        logger.warning(f"Emoji '{emoji_name}' not found for role '{role_value}'")
        return None

    def get_emoji_or_fallback(self, role_value: str) -> str:
        """
        Get emoji string for role, or fallback to role name if emoji not found.

        Args:
            role_value: Role value from Role enum (e.g., "carry", "support")

        Returns:
            Emoji string if found, otherwise the role name in brackets
        """
        # Don't show anything for NONE or FILL roles
        if role_value.lower() in ("none", "fill"):
            return ""

        emoji_str = self.get_emoji_string(role_value)
        if emoji_str:
            return emoji_str
        # Fallback to role name in brackets
        return f"[{role_value.capitalize()}]"
