"""Item data models."""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class ItemAggressionType(str, Enum):
    """Item aggression type enum."""
    ANTI_BURST = "ANTI_BURST"
    ANTI_CRIT = "ANTI_CRIT"
    ANTI_DISRUPTION = "ANTI_DISRUPTION"
    ANTI_HEAL = "ANTI_HEAL"
    ANTI_MAGIC = "ANTI_MAGIC"
    ANTI_SHIELD = "ANTI_SHIELD"
    ANTI_TANK = "ANTI_TANK"
    AREA_DAMAGE = "AREA_DAMAGE"
    ATTACK_SPEED = "ATTACK_SPEED"
    BURST = "BURST"
    CLEANSE = "CLEANSE"
    CRIPPLE = "CRIPPLE"
    CRIT_AMP = "CRIT_AMP"
    CURSED = "CURSED"
    DAMAGE_AMP = "DAMAGE_AMP"
    DEFENSE = "DEFENSE"
    DEFENSIVE_AURA = "DEFENSIVE_AURA"
    DISRUPTION = "DISRUPTION"
    DUELING = "DUELING"
    ENGAGE = "ENGAGE"
    HEALING = "HEALING"
    HEALING_AND_SHIELDING = "HEALING_AND_SHIELDING"
    MAGICAL_PENETRATION = "MAGICAL_PENETRATION"
    MAGICAL_SHRED = "MAGICAL_SHRED"
    MOBILITY = "MOBILITY"
    MULTI_KILL = "MULTI_KILL"
    OFFENSE = "OFFENSE"
    OFFENSIVE_AURA = "OFFENSIVE_AURA"
    ON_HIT = "ON_HIT"
    ON_HIT_AURA = "ON_HIT_AURA"
    PERIODIC_DAMAGE = "PERIODIC_DAMAGE"
    POKE = "POKE"
    PHYSICAL_PENETRATION = "PHYSICAL_PENETRATION"
    PHYSICAL_SHRED = "PHYSICAL_SHRED"
    REDUCED_COOLDOWNS = "REDUCED_COOLDOWNS"
    REFLECT_DAMAGE = "REFLECT_DAMAGE"
    REGEN = "REGEN"
    RESURRECTION = "RESURRECTION"
    SCALING = "SCALING"
    SCALING_HEALTH = "SCALING_HEALTH"
    SCALING_MANA = "SCALING_MANA"
    SHIELDING = "SHIELDING"
    SHRED = "SHRED"
    SLOWING_AURA = "SLOWING_AURA"
    SLOWING_BASICS = "SLOWING_BASICS"
    SLOWING_SPELLS = "SLOWING_SPELLS"
    SPELL_SHIELD = "SPELL_SHIELD"
    SPLITPUSH = "SPLITPUSH"
    STASIS = "STASIS"
    SUSTAIN = "SUSTAIN"
    SUSTAINED_DURABILITY = "SUSTAINED_DURABILITY"
    SUSTAINED_FIGHTING = "SUSTAINED_FIGHTING"
    TEAMFIGHT_DURABILITY = "TEAMFIGHT_DURABILITY"
    TEAMFIGHTING = "TEAMFIGHTING"
    UTILITY = "UTILITY"
    UTILITY_AURA = "UTILITY_AURA"
    ZONE_CONTROL = "ZONE_CONTROL"
    TESTING_OUR_SPACE_WITH_TEXT_123 = "TESTING_OUR_SPACE_WITH_TEXT_123"
    ABILITY_DAMAGE = "ABILITY_DAMAGE"
    ANTI_CARRY = "ANTI_CARRY"
    ANTI_CC = "ANTI_CC"
    ARMOR = "ARMOR"
    ASSASSIN = "ASSASSIN"
    BASIC_ATTACKS = "BASIC_ATTACKS"
    CARRY = "CARRY"
    COOLDOWNS = "COOLDOWNS"
    CRITICAL_STRIKES = "CRITICAL_STRIKES"
    CROUD_CONTROL = "CROUD_CONTROL"
    DAMAGE_OVER_TIME = "DAMAGE_OVER_TIME"
    ENHANCED_ABILITY = "ENHANCED_ABILITY"
    ENHANCED_BLINK = "ENHANCED_BLINK"
    EXECUTIONS = "EXECUTIONS"
    FARMING = "FARMING"
    FIGHTER = "FIGHTER"
    FINISHER = "FINISHER"
    HEALTH_REGEN = "HEALTH_REGEN"
    INCREASED_AMMO = "INCREASED_AMMO"
    INCREASED_GOLD = "INCREASED_GOLD"
    INCREASED_RANGE = "INCREASED_RANGE"
    INCREASED_XP = "INCREASED_XP"
    ISOLATION_DAMAGE = "ISOLATION_DAMAGE"
    JUNGLE = "JUNGLE"
    MAGE = "MAGE"
    MANA_REGEN = "MANA_REGEN"
    OFFLANE = "OFFLANE"
    RELOAD_SPEED = "RELOAD_SPEED"
    SHRINK_EFFECT = "SHRINK_EFFECT"
    SUPPORT = "SUPPORT"
    SUSTAINED_DAMAGE = "SUSTAINED_DAMAGE"
    TAKEDOWNS = "TAKEDOWNS"
    ULTIMATE_DAMAGE = "ULTIMATE_DAMAGE"


class ItemRarity(str, Enum):
    """Item rarity enum."""
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"


class SlotType(str, Enum):
    """Item slot type enum."""
    PASSIVE = "PASSIVE"
    ACTIVE = "ACTIVE"
    CREST = "CREST"
    TRINKET = "TRINKET"


class HeroClass(str, Enum):
    """Hero class enum."""
    NONE = "NONE"
    TANK = "TANK"
    FIGHTER = "FIGHTER"
    ASSASSIN = "ASSASSIN"
    SUPPORT = "SUPPORT"
    SHARPSHOOTER = "SHARPSHOOTER"
    MAGE = "MAGE"
    EXECUTIONER = "EXECUTIONER"
    ENCHANTER = "ENCHANTER"
    WARDEN = "WARDEN"
    CATCHER = "CATCHER"


class ItemDescriptionStat(str, Enum):
    """Item description stat enum."""
    DEFAULT = "DEFAULT"
    HEALTH = "HEALTH"
    BASE_HEALTH_REGENERATION = "BASE_HEALTH_REGENERATION"
    MANA = "MANA"
    BASE_MANA_REGENERATION = "BASE_MANA_REGENERATION"
    PHYSICAL_POWER = "PHYSICAL_POWER"
    MAGICAL_POWER = "MAGICAL_POWER"
    PHYSICAL_ARMOR = "PHYSICAL_ARMOR"
    MAGICAL_ARMOR = "MAGICAL_ARMOR"
    PHYSICAL_PENETRATION = "PHYSICAL_PENETRATION"
    PERC_PHYSICAL_PENETRATION = "PERC_PHYSICAL_PENETRATION"
    MAGICAL_PENETRATION = "MAGICAL_PENETRATION"
    PERC_MAGICAL_PENETRATION = "PERC_MAGICAL_PENETRATION"
    ATTACK_SPEED = "ATTACK_SPEED"
    CRITICAL_CHANCE = "CRITICAL_CHANCE"
    ABILITY_HASTE = "ABILITY_HASTE"
    LIFESTEAL = "LIFESTEAL"
    MAGICAL_LIFESTEAL = "MAGICAL_LIFESTEAL"
    OMNIVAMP = "OMNIVAMP"
    TENACITY = "TENACITY"
    GOLD_PER_SECOND = "GOLD_PER_SECOND"
    MOVEMENT_SPEED = "MOVEMENT_SPEED"
    HEAL_AND_SHIELD_POWER = "HEAL_AND_SHIELD_POWER"


@dataclass(frozen=True)
class ItemStat:
    """Represents an item stat."""
    id: str
    stat: ItemDescriptionStat
    value: float
    show_percent: bool
    
    @classmethod
    def from_api_data(cls, stat_data: dict) -> "ItemStat":
        """Create an ItemStat from API data."""
        return cls(
            id=stat_data.get("id", ""),
            stat=ItemDescriptionStat(stat_data.get("stat", "DEFAULT")),
            value=float(stat_data.get("value", 0.0)),
            show_percent=bool(stat_data.get("showPercent", False))
        )


@dataclass(frozen=True)
class ItemEffect:
    """Represents an item effect."""
    id: str
    name: str
    text: str
    active: bool
    condition: Optional[str] = None
    cooldown: Optional[str] = None
    
    @classmethod
    def from_api_data(cls, effect_data: dict) -> "ItemEffect":
        """Create an ItemEffect from API data."""
        return cls(
            id=effect_data.get("id", ""),
            name=effect_data.get("name", ""),
            text=effect_data.get("text", ""),
            active=bool(effect_data.get("active", False)),
            condition=effect_data.get("condition"),
            cooldown=effect_data.get("cooldown")
        )


@dataclass(frozen=True)
class ItemData:
    """Represents item data for a specific version."""
    id: str
    name: str
    display_name: str
    icon: str
    small_icon: str
    price: int
    total_price: int
    game_id: int
    aggression_type: ItemAggressionType
    class_type: HeroClass
    rarity: ItemRarity
    slot_type: SlotType
    is_evolved: bool
    is_hidden: bool
    stats: List[ItemStat]
    effects: List[ItemEffect]
    # Related items (simplified - just IDs to avoid circular references)
    builds_from_ids: List[str]
    builds_into_ids: List[str]
    blocks_ids: List[str]
    blocked_by_ids: List[str]
    
    @classmethod
    def from_api_data(cls, item_data: dict) -> "ItemData":
        """Create an ItemData from API data."""
        stats = [
            ItemStat.from_api_data(stat) 
            for stat in item_data.get("stats", [])
        ]
        effects = [
            ItemEffect.from_api_data(effect)
            for effect in item_data.get("effects", [])
        ]
        
        # Extract IDs from related items (to avoid circular references)
        builds_from_ids = [
            build_from.get("id", "") 
            for build_from in item_data.get("buildsFrom", [])
        ]
        builds_into_ids = [
            builds_into.get("id", "")
            for builds_into in item_data.get("buildsInto", [])
        ]
        blocks_ids = [
            blocks.get("id", "")
            for blocks in item_data.get("blocks", [])
        ]
        blocked_by_ids = [
            blocked_by.get("id", "")
            for blocked_by in item_data.get("blockedBy", [])
        ]
        
        return cls(
            id=item_data.get("id", ""),
            name=item_data.get("name", ""),
            display_name=item_data.get("displayName", ""),
            icon=item_data.get("icon", ""),
            small_icon=item_data.get("smallIcon", ""),
            price=int(item_data.get("price", 0)),
            total_price=int(item_data.get("totalPrice", 0)),
            game_id=int(item_data.get("gameId", 0)),
            aggression_type=ItemAggressionType(item_data.get("aggressionType", "NONE")),
            class_type=HeroClass(item_data.get("class", "NONE")),
            rarity=ItemRarity(item_data.get("rarity", "COMMON")),
            slot_type=SlotType(item_data.get("slotType", "PASSIVE")),
            is_evolved=bool(item_data.get("isEvolved", False)),
            is_hidden=bool(item_data.get("isHidden", False)),
            stats=stats,
            effects=effects,
            builds_from_ids=builds_from_ids,
            builds_into_ids=builds_into_ids,
            blocks_ids=blocks_ids,
            blocked_by_ids=blocked_by_ids
        )


@dataclass(frozen=True)
class Item:
    """
    Represents an item with its basic information.
    
    Attributes:
        id: The item's unique identifier.
        name: The item's internal name.
        slug: The item's URL slug (optional).
        icon_url: Full URL to the item's icon image.
        icon_asset_id: Asset ID from the GraphQL API (if available).
        data: Optional ItemData for a specific version.
    """
    id: str
    name: str
    slug: Optional[str] = None
    icon_url: Optional[str] = None
    icon_asset_id: Optional[str] = None
    data: Optional[ItemData] = None
    
    @classmethod
    def from_api_data(cls, item_data: dict) -> "Item":
        """
        Create an Item from GraphQL API response data.
        
        Args:
            item_data: Dictionary containing item data from GraphQL API
            
        Returns:
            Item instance with icon URL constructed from asset ID
        """
        item_id = item_data.get("id", "")
        name = item_data.get("name", "")
        slug = item_data.get("slug")
        
        # Extract data if present
        data_dict = item_data.get("data")
        item_data_obj = None
        icon_asset_id = None
        
        if data_dict:
            icon_asset_id = data_dict.get("icon", "")
            item_data_obj = ItemData.from_api_data(data_dict)
        else:
            # Try to get icon from top level if data is not present
            icon_asset_id = item_data.get("icon")
        
        # Construct icon URL from asset ID
        icon_url = None
        if icon_asset_id:
            icon_url = f"https://pred.gg/assets/{icon_asset_id}.png"
        elif slug:
            # Fallback to slug-based URL
            icon_url = f"https://pred.gg/items/{slug}.png"
        
        return cls(
            id=item_id,
            name=name,
            slug=slug,
            icon_url=icon_url,
            icon_asset_id=icon_asset_id if icon_asset_id else None,
            data=item_data_obj
        )


class ItemRegistry:
    """
    Registry for item data, allowing lookup by name, slug, or ID.
    
    This can be populated from the GraphQL API on startup.
    """
    
    def __init__(self) -> None:
        self._items_by_id: dict[str, Item] = {}
        self._items_by_name: dict[str, Item] = {}
        self._items_by_slug: dict[str, Item] = {}
    
    def add_item(self, item: Item) -> None:
        """Add an item to the registry."""
        self._items_by_id[item.id] = item
        self._items_by_name[item.name.lower()] = item
        if item.slug:
            self._items_by_slug[item.slug.lower()] = item
    
    def get_by_id(self, item_id: str) -> Optional[Item]:
        """Get an item by ID."""
        return self._items_by_id.get(item_id)
    
    def get_by_name(self, name: str) -> Optional[Item]:
        """Get an item by name (case-insensitive)."""
        return self._items_by_name.get(name.lower())
    
    def get_by_slug(self, slug: str) -> Optional[Item]:
        """Get an item by slug (case-insensitive)."""
        return self._items_by_slug.get(slug.lower())
    
    def get_icon_url(self, item_name: str) -> str:
        """
        Get icon URL for an item by name.
        
        Falls back to constructing URL from item name if not found in registry.
        
        Args:
            item_name: The item's name
            
        Returns:
            Icon URL for the item
        """
        item = self.get_by_name(item_name)
        if item and item.icon_url:
            return item.icon_url
        
        # Fallback: construct URL from item name (lowercase)
        slug = item_name.lower().replace(" ", "-")
        return f"https://pred.gg/items/{slug}.png"
    
    def get_all(self) -> list[Item]:
        """Get all registered items."""
        return list(self._items_by_id.values())

