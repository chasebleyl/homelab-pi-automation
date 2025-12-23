"""Service for mapping hero names to Discord emojis."""
import logging
from typing import Optional
import discord
from discord import utils

from predecessor_api import name_to_slug

logger = logging.getLogger("belica.hero_emoji")


class HeroEmojiMapper:
    """Maps hero names to Discord emoji references."""
    
    # Mapping from hero names (as they appear in API) to emoji names (as they appear in Discord)
    # Note: Discord removes hyphens from emoji names, so "iggy-scorch" becomes "iggyscorch"
    HERO_NAME_TO_EMOJI_NAME = {
        "Akeron": "akeron",
        "Argus": "argus",
        "Aurora": "aurora",
        "Bayle": "bayle",
        "Boris": "boris",
        "Countess": "countess",
        "Crunch": "crunch",
        "Dekker": "dekker",
        "Drongo": "drongo",
        "Eden": "eden",
        "Feng Mao": "fengmao",
        "Gadget": "gadget",
        "Gideon": "gideon",
        "Greystone": "greystone",
        "Grim.exe": "grimexe",
        "Grux": "grux",
        "Howitzer": "howitzer",
        "Iggy & Scorch": "iggyscorch",
        "Kallari": "kallari",
        "Khaimera": "khaimera",
        "Kira": "kira",
        "Kwang": "kwang",
        "Lt. Belica": "ltbelica",
        "Morigesh": "morigesh",
        "Mourn": "mourn",
        "Murdock": "murdock",
        "Muriel": "muriel",
        "Narbash": "narbash",
        "Phase": "phase",
        "Rampage": "rampage",
        "Renna": "renna",
        "Revenant": "revenant",
        "Riktor": "riktor",
        "Serath": "serath",
        "Sevarog": "sevarog",
        "Shinbi": "shinbi",
        "Skylar": "skylar",
        "Sparrow": "sparrow",
        "Steel": "steel",
        "Terra": "terra",
        "The Fey": "thefey",
        "Twinblast": "twinblast",
        "Wraith": "wraith",
        "Wukong": "wukong",
        "Yin": "yin",
        "Yurei": "yurei",
        "Zarus": "zarus",
        "Zinx": "zinx",
        # Alternative names/variations that might appear in API
        "Wood": "mourn",  # Wood is an alias for Mourn
    }
    
    def __init__(self, guild: Optional[discord.Guild] = None, bot: Optional[discord.Client] = None):
        """
        Initialize the hero emoji mapper.
        
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
        
        This is the proper way to find emojis as shown in:
        https://github.com/Rapptz/discord.py/issues/390
        
        Note: bot.emojis contains guild emojis from all servers.
        Application emojis are fetched separately and stored in bot.application_emojis.
        
        Args:
            emoji_name: The emoji name to search for
            
        Returns:
            The Emoji object if found, None otherwise
        """
        if not self.bot:
            return None
        
        # First, check application emojis (bot-specific, work across all servers)
        # Application emojis are NOT in bot.emojis - they're stored separately
        if hasattr(self.bot, 'application_emojis') and self.bot.application_emojis:
            app_emoji = utils.get(self.bot.application_emojis, name=emoji_name)
            if app_emoji:
                return app_emoji
        
        # Then, check guild emojis (from all servers the bot is in)
        # bot.emojis contains guild emojis from all servers
        guild_emoji = utils.get(self.bot.emojis, name=emoji_name)
        return guild_emoji
    
    def _normalize_hero_name(self, hero_name: str) -> str:
        """
        Normalize hero name for lookup.

        Args:
            hero_name: Hero name from API (e.g., "Countess", "Lt. Belica", "Mourn")

        Returns:
            Normalized hero name for emoji lookup
        """
        # Try direct lookup first
        if hero_name in self.HERO_NAME_TO_EMOJI_NAME:
            return self.HERO_NAME_TO_EMOJI_NAME[hero_name]

        # Try case-insensitive lookup
        hero_name_lower = hero_name.lower()
        for api_name, emoji_name in self.HERO_NAME_TO_EMOJI_NAME.items():
            if api_name.lower() == hero_name_lower:
                return emoji_name

        # Fallback: use shared slug function, then remove hyphens for Discord emoji format
        # Discord emoji names cannot contain hyphens
        slug = name_to_slug(hero_name)
        emoji_name = slug.replace("-", "")
        logger.warning(f"No mapping found for hero '{hero_name}', using fallback: '{emoji_name}'")
        return emoji_name
    
    def get_emoji_string(self, hero_name: str) -> Optional[str]:
        """
        Get the emoji string for a hero name.
        
        Uses discord.utils.get() to find emojis from bot.emojis, following the pattern
        from https://github.com/Rapptz/discord.py/issues/390
        
        Args:
            hero_name: Hero name from API
            
        Returns:
            Emoji string in format <:name:id> or <a:name:id>, or None if not found
        """
        emoji_name = self._normalize_hero_name(hero_name)
        
        # Use discord.utils.get() to find emoji from bot.emojis
        emoji = self._get_emoji_by_name(emoji_name)
        if emoji:
            # Convert emoji to string to get the proper format: <:name:id> or <a:name:id>
            # This is the recommended way as shown in the GitHub issue
            emoji_str = str(emoji)
            logger.debug(f"Found emoji for hero '{hero_name}' (emoji_name='{emoji_name}'): {emoji_str}")
            return emoji_str
        
        # Try case-insensitive search if exact match failed
        if self.bot:
            for bot_emoji in self.bot.emojis:
                if bot_emoji.name.lower() == emoji_name.lower():
                    emoji_str = str(bot_emoji)
                    logger.debug(f"Found emoji for hero '{hero_name}' (case-insensitive, emoji_name='{emoji_name}'): {emoji_str}")
                    return emoji_str
        
        logger.warning(f"Emoji '{emoji_name}' not found in bot.emojis for hero '{hero_name}'")
        if self.bot:
            # Log available emoji names for debugging
            available_names = [e.name for e in self.bot.emojis]
            logger.debug(f"Available emoji names in bot.emojis: {sorted(available_names)[:10]}...")
        return None
    
    def get_emoji_or_fallback(self, hero_name: str) -> str:
        """
        Get emoji string for hero, or fallback to hero name if emoji not found.
        
        Args:
            hero_name: Hero name from API
            
        Returns:
            Emoji string if found, otherwise italicized hero name
        """
        emoji_str = self.get_emoji_string(hero_name)
        if emoji_str:
            return emoji_str
        # Fallback to italicized hero name
        return f"*{hero_name}*"

