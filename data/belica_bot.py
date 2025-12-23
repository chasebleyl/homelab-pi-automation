"""Belica bot data entities for Discord guild configurations."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SubscribedProfile:
    """Entity representing a subscribed player profile for a Discord guild."""
    guild_id: int
    player_uuid: str
    subscribed_at: datetime
    player_name: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict) -> "SubscribedProfile":
        """Create a SubscribedProfile from a database row."""
        return cls(
            guild_id=row["guild_id"],
            player_uuid=row["player_uuid"],
            subscribed_at=row["subscribed_at"],
            player_name=row.get("player_name")
        )


@dataclass
class TargetChannel:
    """Entity representing a target channel for match notifications."""
    guild_id: int
    channel_id: int
    configured_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "TargetChannel":
        """Create a TargetChannel from a database row."""
        return cls(
            guild_id=row["guild_id"],
            channel_id=row["channel_id"],
            configured_at=row["configured_at"]
        )
