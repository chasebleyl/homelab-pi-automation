"""Service for fetching recent matches from the Predecessor API."""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from predecessor_api import PredecessorAPI, PlayerMatchesService

logger = logging.getLogger("crons.match_fetcher")


class MatchFetcher:
    """Service for fetching recent matches from the Predecessor API."""
    
    def __init__(self, api: PredecessorAPI) -> None:
        """
        Initialize the match fetcher.
        
        Args:
            api: PredecessorAPI client instance
        """
        self.api = api
        self.player_matches_service = PlayerMatchesService(api)
    
    async def fetch_recent_matches_by_timeframe(
        self,
        start_time: datetime,
        end_time: datetime,
        player_uuids: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Fetch recent matches within a time frame.
        
        Note: The Predecessor API doesn't have a direct "all recent matches" endpoint.
        This method queries by known players and filters by timeframe.
        
        Args:
            start_time: Start of the time range
            end_time: End of the time range
            player_uuids: Optional list of player UUIDs to query (if None, returns empty list)
            limit: Maximum number of matches to fetch per player
            
        Returns:
            List of match data dictionaries (deduplicated by match UUID)
        """
        if not player_uuids:
            logger.warning("No player UUIDs provided, returning empty list")
            return []
        
        matches = await self.player_matches_service.fetch_matches_for_multiple_players(
            player_uuids=player_uuids,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        logger.info(f"Fetched {len(matches)} unique matches in timeframe {start_time} to {end_time}")
        return matches
    
    async def fetch_recent_matches_by_interval(
        self,
        interval_minutes: int,
        player_uuids: Optional[List[str]] = None
    ) -> List[dict]:
        """
        Fetch matches from the last N minutes.

        Args:
            interval_minutes: How many minutes back to look
            player_uuids: Optional list of player UUIDs to query

        Returns:
            List of match data dictionaries
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=interval_minutes)

        return await self.fetch_recent_matches_by_timeframe(
            start_time,
            end_time,
            player_uuids=player_uuids
        )

    async def fetch_matches_for_player(
        self,
        player_uuid: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100
    ) -> List[dict]:
        """
        Fetch matches for a single player within a time range.

        Args:
            player_uuid: The player's UUID
            start_time: Start of the time range
            end_time: End of the time range
            limit: Maximum number of matches to fetch

        Returns:
            List of match data dictionaries
        """
        matches = await self.player_matches_service.fetch_player_matches(
            player_uuid=player_uuid,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        logger.info(
            f"Fetched {len(matches)} matches for player {player_uuid} "
            f"from {start_time} to {end_time}"
        )
        return matches

