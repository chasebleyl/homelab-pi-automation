"""Predecessor-related data entities."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProcessedMatch:
    """Entity representing a processed match."""
    match_uuid: str
    match_id: str
    end_time: datetime
    processed_at: datetime
    notified_bot: bool = False

    @classmethod
    def from_row(cls, row: dict) -> "ProcessedMatch":
        """Create a ProcessedMatch from a database row."""
        return cls(
            match_uuid=row["match_uuid"],
            match_id=row["match_id"],
            end_time=row["end_time"],
            processed_at=row["processed_at"],
            notified_bot=row["notified_bot"]
        )


@dataclass
class PlayerMatchCursor:
    """Entity representing a player's match fetch cursor."""
    player_uuid: str
    last_match_end_time: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "PlayerMatchCursor":
        """Create a PlayerMatchCursor from a database row."""
        return cls(
            player_uuid=row["player_uuid"],
            last_match_end_time=row["last_match_end_time"],
            updated_at=row["updated_at"]
        )
