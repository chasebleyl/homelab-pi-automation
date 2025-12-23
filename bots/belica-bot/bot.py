"""Belica Discord Bot - Main entry point."""
import asyncio
import logging
import os
import discord
from discord.ext import commands

from config import Config
from predecessor_api import PredecessorAPI, HeroRegistry, HeroService, MatchService
from services.channel_config_db import ChannelConfig
from services.profile_subscription_db import ProfileSubscription
from services.http_server import HTTPServer
from services.match_formatter import ScoreboardButton

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
        
        self.api = PredecessorAPI(
            api_url=Config.PRED_GG_API_URL,
            oauth_token_url=Config.PRED_GG_OAUTH_API_URL or None,
            client_id=Config.PRED_GG_CLIENT_ID or None,
            client_secret=Config.PRED_GG_CLIENT_SECRET or None,
        )
        self.hero_registry = HeroRegistry()
        self.hero_service = HeroService(self.api)
        self.match_service = MatchService(self.api, self.hero_registry)
        self.channel_config = ChannelConfig()
        self.profile_subscription = ProfileSubscription()
        self.application_emojis: list[discord.Emoji] = []  # Cache application emojis
        self.http_server: HTTPServer | None = None
    
    async def setup_hook(self) -> None:
        """Called when the bot is starting up."""
        # Populate hero registry from API
        logger.info("Populating hero registry...")
        try:
            await self.hero_service.populate_hero_registry(self.hero_registry)
            hero_count = len(self.hero_registry.get_all())
            logger.info(f"Hero registry populated with {hero_count} heroes")
        except Exception as e:
            logger.warning(f"Failed to populate hero registry: {e}")
        
        # Load cogs
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.matches")
        logger.info("Loaded cogs")

        # Register dynamic items for persistent button handling after bot restarts
        self.add_dynamic_items(ScoreboardButton)
        logger.info("Registered dynamic items for persistent buttons")

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
        
        # Start HTTP server for receiving match notifications
        http_port = int(os.getenv("HTTP_PORT", "8080"))
        self.http_server = HTTPServer(self, port=http_port)
        await self.http_server.start()

    async def is_target_channel(self, channel: discord.TextChannel) -> bool:
        """
        Check if a channel is configured as a target channel for posting.
        
        Args:
            channel: The Discord text channel to check
            
        Returns:
            True if the channel is configured, False otherwise
        """
        if not channel.guild:
            return False
        return await self.channel_config.is_target_channel(channel.guild.id, channel.id)
    
    async def close(self) -> None:
        """Clean up resources when shutting down."""
        if self.http_server:
            await self.http_server.stop()
        if self.profile_subscription:
            await self.profile_subscription.close()
        if self.channel_config:
            await self.channel_config.close()
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

