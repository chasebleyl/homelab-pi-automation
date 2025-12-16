"""Service for fetching and transforming match data from the GraphQL API."""
import logging
from datetime import datetime, timezone
from typing import Optional

from api import PredecessorAPI
from models import MatchData, MatchPlayerData, TeamSide, GameMode, Region
from models.hero import HeroRegistry

logger = logging.getLogger("belica.match_service")


class MatchService:
    """Service for fetching and processing match data from the Predecessor API."""
    
    # GraphQL query for fetching match data
    GET_MATCH_QUERY = """
    query GetMatch($matchKey: MatchKey!) {
        match(by: $matchKey) {
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
    """
    
    def __init__(self, api: PredecessorAPI, hero_registry: Optional[HeroRegistry] = None) -> None:
        """
        Initialize the match service.
        
        Args:
            api: PredecessorAPI client instance
            hero_registry: Optional hero registry for icon URL resolution
        """
        self.api = api
        self.hero_registry = hero_registry
    
    def normalize_match_id(self, match_id: str) -> dict:
        """
        Normalize match ID to MatchKey format for GraphQL query.
        
        Handles:
        - UUID with dashes: "440d3105-6a25-465c-9c47-23129ec6d453"
        - UUID without dashes: "440d31056a25465c9c4723129ec6d453"
        - Numeric ID: "12345"
        
        Args:
            match_id: The match ID string
            
        Returns:
            MatchKey dictionary for GraphQL query
        """
        # Remove dashes if present
        clean_id = match_id.replace("-", "")
        
        # Check if it's a UUID (32 hex characters)
        if len(clean_id) == 32 and all(c in "0123456789abcdefABCDEF" for c in clean_id):
            # It's a UUID - format with dashes
            formatted_uuid = f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"
            return {"id": formatted_uuid}
        else:
            # Assume it's a numeric ID
            return {"id": match_id}
    
    async def fetch_match(self, match_id: str) -> Optional[MatchData]:
        """
        Fetch match data from the API and transform it to MatchData.
        
        Args:
            match_id: The match ID (UUID or numeric)
            
        Returns:
            MatchData instance if found, None otherwise
            
        Raises:
            Exception: If there's an error fetching from the API
        """
        # Normalize match ID
        match_key = self.normalize_match_id(match_id.strip())
        
        # Fetch match data
        result = await self.api.query(self.GET_MATCH_QUERY, {"matchKey": match_key})
        match_data = result.get("match")
        
        if not match_data:
            return None
        
        # Transform to MatchData model
        return self.transform_match_data(match_data)
    
    def transform_match_data(self, match_data: dict) -> MatchData:
        """
        Transform GraphQL match data to MatchData model.
        
        Args:
            match_data: Raw match data from GraphQL API
            
        Returns:
            MatchData instance
        """
        # Parse match metadata
        match_uuid = match_data.get("uuid", "")
        match_id_str = match_data.get("id", match_uuid)
        duration_seconds = match_data.get("duration", 0)
        end_time_str = match_data.get("endTime", "")
        game_mode_str = match_data.get("gameMode", "NONE")
        region_str = match_data.get("region", "NONE")
        winning_team_str = match_data.get("winningTeam", "NONE")
        
        # Parse end time
        # GraphQL DateTime is ISO 8601 format
        try:
            end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            end_time = datetime.now(timezone.utc)
        
        # Map enums
        game_mode = self._map_game_mode(game_mode_str)
        region = self._map_region(region_str)
        winning_team = self._map_team_side(winning_team_str)
        
        # Process players
        match_players = match_data.get("matchPlayers", [])
        players = []
        dawn_kills = 0
        dusk_kills = 0
        
        for mp in match_players:
            player_data = mp.get("player") or {}
            hero_data = mp.get("hero") or {}
            hero_data_versioned = mp.get("heroData") or {}
            team_str = mp.get("team", "NONE")
            
            player_name = player_data.get("name", "Unknown") if player_data else "Unknown"
            player_uuid = player_data.get("uuid", "") if player_data else ""
            
            # Prefer heroData (version-specific) over hero, fallback to "Unknown"
            if hero_data_versioned:
                hero_name = hero_data_versioned.get("displayName") or hero_data_versioned.get("name", "Unknown")
            elif hero_data:
                hero_name = hero_data.get("name", "Unknown")
            else:
                hero_name = "Unknown"
                logger.warning(f"No hero data found for player {player_name}")
            
            team = self._map_team_side(team_str)
            
            kills = mp.get("kills", 0)
            deaths = mp.get("deaths", 0)
            assists = mp.get("assists", 0)
            
            # Count kills per team
            if team == TeamSide.DAWN:
                dawn_kills += kills
            elif team == TeamSide.DUSK:
                dusk_kills += kills
            
            # Get MMR change from rating if available
            rating = mp.get("rating")
            mmr_change = None
            if rating:
                new_points = rating.get("newPoints", 0)
                old_points = rating.get("points", 0)
                mmr_change = int(new_points - old_points)
            
            # Get hero icon URL - prefer icon from heroData if available
            if hero_data_versioned and hero_data_versioned.get("icon"):
                icon_asset_id = hero_data_versioned.get("icon")
                hero_icon_url = f"https://pred.gg/assets/{icon_asset_id}.png"
            else:
                hero_icon_url = self._get_hero_icon_url(hero_name)
            
            # Note: is_opted_in is not available from API, so we default to False
            # Subscribed profiles will be included via the formatter
            player = MatchPlayerData(
                player_name=player_name,
                player_uuid=player_uuid,
                hero_name=hero_name,
                hero_icon_url=hero_icon_url,
                team=team,
                kills=kills,
                deaths=deaths,
                assists=assists,
                mmr_change=mmr_change,
                performance_score=None,  # Not available in API
                is_opted_in=False,  # Not available in API
            )
            players.append(player)
        
        return MatchData(
            match_uuid=match_uuid,
            match_id=match_id_str,
            duration_seconds=duration_seconds,
            game_mode=game_mode,
            region=region,
            winning_team=winning_team,
            dawn_score=dawn_kills,
            dusk_score=dusk_kills,
            end_time=end_time,
            players=tuple(players),
        )
    
    def _map_game_mode(self, game_mode_str: str) -> GameMode:
        """Map GraphQL GameMode enum to our GameMode enum."""
        mapping = {
            "RANKED": GameMode.RANKED,
            "STANDARD": GameMode.STANDARD,
            "CUSTOM": GameMode.CUSTOM,
            "PRACTICE": GameMode.PRACTICE,
            "SOLO": GameMode.SOLO,
            "ARENA": GameMode.ARENA,
            "RUSH": GameMode.RUSH,
            "ARAM": GameMode.ARAM,
        }
        return mapping.get(game_mode_str, GameMode.STANDARD)
    
    def _map_region(self, region_str: str) -> Region:
        """Map GraphQL Region enum to our Region enum."""
        mapping = {
            "EUROPE": Region.EUROPE,
            "NA_EAST": Region.NA_EAST,
            "NA_WEST": Region.NA_WEST,
            "NA": Region.NA,
            "ASIA": Region.ASIA,
            "OCE": Region.OCE,
            "SEA": Region.SEA,
            "MENA": Region.MENA,
            "SA": Region.SA,
        }
        return mapping.get(region_str, Region.NA)
    
    def _map_team_side(self, team_str: str) -> TeamSide:
        """Map GraphQL MatchPlayerTeam enum to our TeamSide enum."""
        if team_str == "DAWN":
            return TeamSide.DAWN
        elif team_str == "DUSK":
            return TeamSide.DUSK
        else:
            return TeamSide.DAWN  # Default fallback
    
    def _get_hero_icon_url(self, hero_name: str) -> str:
        """
        Get the correct icon URL for a hero by name.
        
        Uses hero registry if available, otherwise falls back to a placeholder.
        
        Args:
            hero_name: The hero's name
            
        Returns:
            Icon URL for the hero
        """
        if self.hero_registry:
            return self.hero_registry.get_icon_url(hero_name)
        # Fallback if registry not available (shouldn't happen in normal operation)
        return f"https://pred.gg/assets/placeholder.png"

