"""Service for fetching player matches from the Predecessor GraphQL API."""
import logging
from datetime import datetime
from typing import List, Optional

from .client import PredecessorAPI

logger = logging.getLogger("predecessor_api.player_matches_service")


class PlayerMatchesService:
    """Service for fetching player matches from the Predecessor API."""
    
    # GraphQL query for fetching recent matches by player
    GET_PLAYER_MATCHES_QUERY = """
    query GetPlayerMatches($playerKey: PlayerKey!, $filter: PlayerMatchesFilterInput, $limit: Int, $offset: Int) {
        player(by: $playerKey) {
            matchesPaginated(filter: $filter, limit: $limit, offset: $offset) {
                results {
                    match {
                        id
                        uuid
                        duration
                        endTime
                        gameMode
                        region
                        winningTeam
                        matchPlayers {
                            player {
                                uuid
                                name
                            }
                            hero {
                                name
                            }
                            heroData {
                                name
                                displayName
                                icon
                            }
                            team
                            kills
                            deaths
                            assists
                            rating {
                                points
                                newPoints
                            }
                        }
                    }
                }
                totalCount
            }
        }
    }
    """
    
    def __init__(self, api: PredecessorAPI) -> None:
        """
        Initialize the player matches service.
        
        Args:
            api: PredecessorAPI client instance
        """
        self.api = api
    
    async def fetch_player_matches(
        self,
        player_uuid: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """
        Fetch matches for a specific player.
        
        Args:
            player_uuid: The player's UUID
            start_time: Optional start time for filtering matches
            end_time: Optional end time for filtering matches
            limit: Maximum number of matches to fetch
            offset: Offset for pagination
            
        Returns:
            List of match data dictionaries (raw GraphQL response format)
        """
        variables: dict = {
            "playerKey": {"uuid": player_uuid},
            "limit": limit,
            "offset": offset
        }
        
        # Add timeframe filter if provided
        if start_time or end_time:
            filter_dict: dict = {}
            if start_time or end_time:
                timeframe: dict = {}
                if start_time:
                    timeframe["startTime"] = start_time.isoformat()
                if end_time:
                    timeframe["endTime"] = end_time.isoformat()
                filter_dict["timeframe"] = timeframe
            variables["filter"] = filter_dict
        
        try:
            result = await self.api.query(self.GET_PLAYER_MATCHES_QUERY, variables)
            
            player_data = result.get("player", {})
            matches_paginated = player_data.get("matchesPaginated", {})
            match_results = matches_paginated.get("results", [])
            
            # Extract match data from results
            matches = []
            for match_player in match_results:
                match_data = match_player.get("match")
                if match_data:
                    matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.warning(f"Failed to fetch matches for player {player_uuid}: {e}")
            return []
    
    async def fetch_player_matches_by_timeframe(
        self,
        player_uuid: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100
    ) -> List[dict]:
        """
        Fetch matches for a player within a specific time frame.
        
        Args:
            player_uuid: The player's UUID
            start_time: Start of the time range
            end_time: End of the time range
            limit: Maximum number of matches to fetch
            
        Returns:
            List of match data dictionaries
        """
        return await self.fetch_player_matches(
            player_uuid=player_uuid,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    
    async def fetch_matches_for_multiple_players(
        self,
        player_uuids: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Fetch matches for multiple players and deduplicate by match UUID.
        
        Args:
            player_uuids: List of player UUIDs to query
            start_time: Optional start time for filtering matches
            end_time: Optional end time for filtering matches
            limit: Maximum number of matches to fetch per player
            
        Returns:
            List of unique match data dictionaries (deduplicated by match UUID)
        """
        all_matches = []
        seen_uuids = set()
        
        for player_uuid in player_uuids:
            matches = await self.fetch_player_matches(
                player_uuid=player_uuid,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
            for match_data in matches:
                match_uuid = match_data.get("uuid")
                if match_uuid and match_uuid not in seen_uuids:
                    seen_uuids.add(match_uuid)
                    all_matches.append(match_data)
        
        return all_matches






