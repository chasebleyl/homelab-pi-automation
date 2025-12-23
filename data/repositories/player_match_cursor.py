"""Repository for player match cursor data."""
import logging
from typing import Optional
from datetime import datetime

from ..connection import Database
from ..predecessor import PlayerMatchCursor

logger = logging.getLogger("data.repositories.player_match_cursor")


class PlayerMatchCursorRepository:
    """Repository for player match cursor data."""

    def __init__(self, db: Database) -> None:
        """
        Initialize the repository.

        Args:
            db: Database connection instance
        """
        self.db = db

    async def get_cursor(self, player_uuid: str) -> Optional[PlayerMatchCursor]:
        """
        Get the match cursor for a player.

        Args:
            player_uuid: The player's UUID

        Returns:
            PlayerMatchCursor if exists, None otherwise
        """
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM player_match_cursors WHERE player_uuid = $1",
                player_uuid
            )
            if row:
                return PlayerMatchCursor.from_row(dict(row))
            return None

    async def get_last_match_time(self, player_uuid: str) -> Optional[datetime]:
        """
        Get the last match end time for a player.

        Args:
            player_uuid: The player's UUID

        Returns:
            The last match end time if exists, None otherwise
        """
        async with self.db.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT last_match_end_time FROM player_match_cursors WHERE player_uuid = $1",
                player_uuid
            )
            return result

    async def update_cursor(self, player_uuid: str, last_match_end_time: datetime) -> None:
        """
        Update or insert the match cursor for a player.

        Args:
            player_uuid: The player's UUID
            last_match_end_time: The end time of the latest match
        """
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO player_match_cursors (player_uuid, last_match_end_time, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (player_uuid) DO UPDATE
                SET last_match_end_time = EXCLUDED.last_match_end_time,
                    updated_at = NOW()
            """, player_uuid, last_match_end_time)

    async def get_all_cursors(self) -> list[PlayerMatchCursor]:
        """Get all player match cursors."""
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM player_match_cursors ORDER BY updated_at DESC"
            )
            return [PlayerMatchCursor.from_row(dict(row)) for row in rows]

    async def delete_cursor(self, player_uuid: str) -> bool:
        """
        Delete the match cursor for a player.

        Args:
            player_uuid: The player's UUID

        Returns:
            True if cursor was deleted, False if it didn't exist
        """
        async with self.db.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM player_match_cursors WHERE player_uuid = $1",
                player_uuid
            )
            return result == "DELETE 1"
