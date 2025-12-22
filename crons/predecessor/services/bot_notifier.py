"""Service for notifying belica-bot about new matches."""
import logging
import aiohttp
from typing import Optional

from config import Config

logger = logging.getLogger("crons.bot_notifier")


class BotNotifier:
    """Service for sending match notifications to belica-bot."""
    
    def __init__(self) -> None:
        """Initialize the bot notifier."""
        self.bot_url = Config.BELICA_BOT_URL
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def notify_match(self, match_data: dict) -> bool:
        """
        Send a match notification to belica-bot.
        
        Args:
            match_data: Match data dictionary from the API
            
        Returns:
            True if notification was successful, False otherwise
        """
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.bot_url}/api/matches",
                json=match_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully notified bot about match {match_data.get('uuid')}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Bot notification failed for match {match_data.get('uuid')}: "
                        f"HTTP {response.status} - {error_text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error notifying bot about match {match_data.get('uuid')}: {e}")
            return False

