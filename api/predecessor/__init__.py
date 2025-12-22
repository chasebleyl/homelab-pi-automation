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
from .match_models import MatchData, MatchPlayerData, TeamSide, GameMode, Region
from .match_service import MatchService
from .hero_service import HeroService
from .item_service import ItemService
from .player_matches_service import PlayerMatchesService

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
    "MatchService",
    "HeroService",
    "ItemService",
    "PlayerMatchesService",
]

