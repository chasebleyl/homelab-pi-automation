"""Shared data layer package for database and data entity management."""
from .config import DatabaseConfig
from .connection import Database
from .predecessor import ProcessedMatch, PlayerMatchCursor
from .belica_bot import SubscribedProfile, TargetChannel
from .repositories import (
    ProcessedMatchRepository,
    SubscribedProfileRepository,
    TargetChannelRepository,
    PlayerMatchCursorRepository,
)

__all__ = [
    # Config & Connection
    "DatabaseConfig",
    "Database",
    # Entities
    "ProcessedMatch",
    "PlayerMatchCursor",
    "SubscribedProfile",
    "TargetChannel",
    # Repositories
    "ProcessedMatchRepository",
    "PlayerMatchCursorRepository",
    "SubscribedProfileRepository",
    "TargetChannelRepository",
]

