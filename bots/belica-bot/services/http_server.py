"""HTTP server for receiving match notifications from cron workers."""
import logging
import aiohttp
from aiohttp import web
from typing import Optional

from predecessor_api import MatchService
from services.match_formatter import MatchMessageFormatter
from services.hero_emoji_mapper import HeroEmojiMapper
from services.role_emoji_mapper import RoleEmojiMapper
from services.profile_subscription_db import ProfileSubscription

logger = logging.getLogger("belica.http_server")


class HTTPServer:
    """HTTP server for receiving match notifications."""
    
    def __init__(
        self,
        bot,
        host: str = "0.0.0.0",
        port: int = 8080
    ) -> None:
        """
        Initialize the HTTP server.
        
        Args:
            bot: The Discord bot instance
            host: Host to bind to
            port: Port to bind to
        """
        self.bot = bot
        self.host = host
        self.port = port
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
    
    async def _handle_match_notification(self, request: web.Request) -> web.Response:
        """
        Handle POST /api/matches - receives match data from cron workers.
        
        Expected JSON body:
        {
            "uuid": "...",
            "id": "...",
            "endTime": "...",
            "gameMode": "...",
            "region": "...",
            "winningTeam": "...",
            "matchPlayers": [...]
        }
        """
        try:
            # Parse request body
            match_data = await request.json()
            
            if not match_data:
                return web.json_response(
                    {"error": "Missing match data"},
                    status=400
                )
            
            logger.info(f"Received match notification: {match_data.get('uuid')}")
            
            # Transform match data using MatchService
            match_service = MatchService(
                self.bot.api,
                self.bot.hero_registry
            )
            
            match = match_service.transform_match_data(match_data)
            
            # Post to all configured channels
            await self._post_match_to_channels(match)
            
            return web.json_response(
                {"status": "success", "match_uuid": match.match_uuid}
            )
        
        except Exception as e:
            logger.error(f"Error handling match notification: {e}", exc_info=True)
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def _post_match_to_channels(self, match) -> None:
        """
        Post match data to all configured Discord channels.
        
        Args:
            match: MatchData instance
        """
        # Get all configured channels
        channel_config = getattr(self.bot, 'channel_config', None)
        if not channel_config:
            logger.warning("Channel config not available")
            return
        
        # Get all target channels
        target_channels = await channel_config.get_all_target_channels()
        
        if not target_channels:
            logger.info("No target channels configured")
            return
        
        logger.info(f"Posting match to {len(target_channels)} channel(s)")
        
        for guild_id, channel_id in target_channels:
            try:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    logger.warning(f"Guild {guild_id} not found")
                    continue
                
                channel = guild.get_channel(channel_id)
                if not channel:
                    logger.warning(f"Channel {channel_id} not found in guild {guild_id}")
                    continue
                
                # Get subscribed profiles for this guild
                profile_subscription: Optional[ProfileSubscription] = getattr(
                    self.bot,
                    'profile_subscription',
                    None
                )
                subscribed_uuids = None
                if profile_subscription:
                    subscribed_uuids = set(await profile_subscription.get_profiles(guild_id))
                
                # Create emoji mappers
                hero_emoji_mapper = HeroEmojiMapper(guild=guild, bot=self.bot)
                role_emoji_mapper = RoleEmojiMapper(guild=guild, bot=self.bot)

                # Format and send match
                formatter = MatchMessageFormatter(
                    match,
                    subscribed_uuids,
                    hero_emoji_mapper,
                    role_emoji_mapper
                )
                
                embed = formatter.create_embed()
                view = formatter.create_view()
                
                await channel.send(embed=embed, view=view)
                logger.info(f"Posted match {match.match_uuid} to channel {channel_id} in guild {guild_id}")
            
            except Exception as e:
                logger.error(
                    f"Error posting match to channel {channel_id} in guild {guild_id}: {e}",
                    exc_info=True
                )
    
    async def start(self) -> None:
        """Start the HTTP server."""
        self.app = web.Application()
        self.app.router.add_post("/api/matches", self._handle_match_notification)
        
        # Health check endpoint
        self.app.router.add_get("/health", self._handle_health)
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        logger.info(f"HTTP server started on {self.host}:{self.port}")
    
    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({"status": "healthy"})
    
    async def stop(self) -> None:
        """Stop the HTTP server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("HTTP server stopped")

