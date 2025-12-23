"""Predecessor GraphQL API client package."""
from .client import PredecessorAPI
from .models import Hero, HeroRegistry
from .item_models import (
    Item,
    ItemData,
    ItemStat,
    ItemEffect,
    ItemRegistry,
    ItemAggressionType,
    ItemRarity,
    SlotType,
    HeroClass,
    ItemDescriptionStat,
)
from .match_models import MatchData, MatchPlayerData, TeamSide, GameMode, Region, Role
from .match_service import MatchService
from .hero_service import HeroService
from .item_service import ItemService
from .player_matches_service import PlayerMatchesService
from .player_service import PlayerService, PlayerInfo
from .utils import format_player_display_name, calculate_per_minute, name_to_slug

__all__ = [
    "PredecessorAPI",
    "Hero",
    "HeroRegistry",
    "Item",
    "ItemData",
    "ItemStat",
    "ItemEffect",
    "ItemRegistry",
    "ItemAggressionType",
    "ItemRarity",
    "SlotType",
    "HeroClass",
    "ItemDescriptionStat",
    "MatchData",
    "MatchPlayerData",
    "TeamSide",
    "GameMode",
    "Region",
    "Role",
    "MatchService",
    "HeroService",
    "ItemService",
    "PlayerMatchesService",
    "PlayerService",
    "PlayerInfo",
    "format_player_display_name",
    "calculate_per_minute",
    "name_to_slug",
]

