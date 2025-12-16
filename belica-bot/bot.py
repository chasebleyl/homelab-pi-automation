"""Belica Discord Bot - Main entry point."""
import asyncio
import logging
import discord
from discord.ext import commands

from config import Config
from api import PredecessorAPI
from services.hero_registry import get_hero_registry, populate_hero_registry
from services import ChannelConfig, ProfileSubscription

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("belica")


class BelicaBot(commands.Bot):
    """Main bot class with Predecessor API integration."""
    
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            description="Predecessor stats and information bot"
        )
        
        self.api = PredecessorAPI(Config.PRED_API_URL)
        self.hero_registry = get_hero_registry()
        self.channel_config = ChannelConfig()
        self.profile_subscription = ProfileSubscription()
        self.application_emojis: list[discord.Emoji] = []  # Cache application emojis
    
    async def setup_hook(self) -> None:
        """Called when the bot is starting up."""
        # Populate hero registry from API
        logger.info("Populating hero registry...")
        try:
            await populate_hero_registry(self.api, self.hero_registry)
            hero_count = len(self.hero_registry.get_all())
            logger.info(f"Hero registry populated with {hero_count} heroes")
        except Exception as e:
            logger.warning(f"Failed to populate hero registry: {e}")
        
        # Load cogs
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.matches")
        logger.info("Loaded cogs")
        
        # Sync slash commands
        if Config.TEST_GUILD_ID:
            # Fast guild-specific sync for development/testing
            test_guild = discord.Object(id=int(Config.TEST_GUILD_ID))
            self.tree.copy_global_to(guild=test_guild)
            await self.tree.sync(guild=test_guild)
            logger.info(f"Synced slash commands to test guild {Config.TEST_GUILD_ID} (fast sync)")
        else:
            # Global sync (slower but works for all servers)
            await self.tree.sync()
            logger.info("Synced slash commands globally")
    
    async def on_ready(self) -> None:
        """Called when the bot has connected to Discord."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Log emoji information for debugging
        # bot.emojis contains all emojis from all guilds the bot is in
        # Application emojis (bot-specific) may need to be fetched separately
        logger.info(f"Bot has access to {len(self.emojis)} emoji(s) from guilds")
        if self.emojis:
            sample_emoji_names = [e.name for e in list(self.emojis)[:5]]
            logger.debug(f"Sample emoji names in bot.emojis: {sample_emoji_names}")
        
        # Try to fetch application emojis if available
        # Application emojis are NOT in bot.emojis - they need to be fetched separately
        try:
            app_emojis = await self.fetch_application_emojis()
            self.application_emojis = list(app_emojis)  # Cache them for the mapper
            if app_emojis:
                app_emoji_names = [e.name for e in app_emojis]
                logger.info(f"Found {len(app_emojis)} application emoji(s): {', '.join(app_emoji_names)}")
            else:
                logger.info("Found 0 application emoji(s)")
        except Exception as e:
            logger.debug(f"Could not fetch application emojis (may not be available): {e}")
            self.application_emojis = []
        
        # Set bot presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Predecessor matches"
        )
        await self.change_presence(activity=activity)
    
    def is_target_channel(self, channel: discord.TextChannel) -> bool:
        """
        Check if a channel is configured as a target channel for posting.
        
        Args:
            channel: The Discord text channel to check
            
        Returns:
            True if the channel is configured, False otherwise
        """
        if not channel.guild:
            return False
        return self.channel_config.is_target_channel(channel.guild.id, channel.id)
    
    async def close(self) -> None:
        """Clean up resources when shutting down."""
        await self.api.close()
        await super().close()


async def main() -> None:
    """Main entry point."""
    Config.validate()
    
    bot = BelicaBot()
    
    async with bot:
        await bot.start(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())

