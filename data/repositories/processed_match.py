"""Repository for processed match data."""
import logging
from typing import Optional
from datetime import datetime

from ..connection import Database
from ..predecessor import ProcessedMatch

logger = logging.getLogger("data.repositories.processed_match")


class ProcessedMatchRepository:
    """Repository for processed match data."""

    def __init__(self, db: Database) -> None:
        """
        Initialize the repository.

        Args:
            db: Database connection instance
        """
        self.db = db

    async def is_match_processed(self, match_uuid: str) -> bool:
        """Check if a match has already been processed."""
        async with self.db.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM processed_matches WHERE match_uuid = $1)",
                match_uuid
            )
            return bool(result)

    async def mark_match_processed(
        self,
        match_uuid: str,
        match_id: str,
        end_time: str | datetime
    ) -> None:
        """
        Mark a match as processed.

        Args:
            match_uuid: The match UUID
            match_id: The match ID
            end_time: The match end time (ISO string or datetime)
        """
        # Convert string to datetime if needed (asyncpg requires datetime objects)
        if isinstance(end_time, str):
            # Handle ISO format with Z suffix
            if end_time.endswith("Z"):
                end_time = end_time[:-1] + "+00:00"
            end_time = datetime.fromisoformat(end_time)

        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO processed_matches (match_uuid, match_id, end_time)
                VALUES ($1, $2, $3)
                ON CONFLICT (match_uuid) DO NOTHING
            """, match_uuid, match_id, end_time)

    async def mark_match_notified(self, match_uuid: str) -> None:
        """Mark a match as having been notified to the bot."""
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                UPDATE processed_matches
                SET notified_bot = TRUE
                WHERE match_uuid = $1
            """, match_uuid)

    async def get_match(self, match_uuid: str) -> Optional[ProcessedMatch]:
        """Get a processed match by UUID."""
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM processed_matches WHERE match_uuid = $1",
                match_uuid
            )
            if row:
                return ProcessedMatch.from_row(dict(row))
            return None

    async def get_unnotified_matches(self, limit: Optional[int] = None) -> list[ProcessedMatch]:
        """Get matches that haven't been notified to the bot yet."""
        query = "SELECT * FROM processed_matches WHERE notified_bot = FALSE ORDER BY processed_at ASC"
        if limit:
            query += f" LIMIT {limit}"

        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [ProcessedMatch.from_row(dict(row)) for row in rows]
