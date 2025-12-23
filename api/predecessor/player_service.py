"""Service for player profile operations."""
import logging
from dataclasses import dataclass
from typing import Optional

from .client import PredecessorAPI

logger = logging.getLogger("predecessor_api.player_service")


@dataclass
class PlayerInfo:
    """Basic player information returned from validation."""
    uuid: str
    name: Optional[str]
    id: str


class PlayerService:
    """Service for validating and fetching player profile information."""

    # GraphQL query to validate a player exists and get basic info
    VALIDATE_PLAYER_QUERY = """
        query ValidatePlayer($playerKey: PlayerKey!) {
            player(by: $playerKey) {
                id
                uuid
                name
            }
        }
    """

    def __init__(self, api: PredecessorAPI) -> None:
        """
        Initialize the player service.

        Args:
            api: PredecessorAPI client instance
        """
        self.api = api

    async def validate_player(self, player_uuid: str) -> Optional[PlayerInfo]:
        """
        Validate that a player UUID exists and fetch their basic info.

        Args:
            player_uuid: The player's UUID

        Returns:
            PlayerInfo if the player exists, None otherwise
        """
        variables = {
            "playerKey": {
                "uuid": player_uuid
            }
        }

        try:
            result = await self.api.query(self.VALIDATE_PLAYER_QUERY, variables)
            player_data = result.get("player")

            if player_data is None:
                logger.debug(f"Player not found: {player_uuid}")
                return None

            return PlayerInfo(
                uuid=player_data["uuid"],
                name=player_data.get("name"),
                id=player_data["id"]
            )

        except Exception as e:
            logger.error(f"Error validating player {player_uuid}: {e}")
            raise
