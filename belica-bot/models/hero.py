"""Hero data models."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Hero:
    """
    Represents a hero with their icon URL.
    
    Attributes:
        name: The hero's internal name (e.g., "Countess").
        display_name: The hero's display name (e.g., "Countess").
        slug: The hero's URL slug (e.g., "countess").
        icon_url: Full URL to the hero's icon image.
        icon_asset_id: Asset ID from the GraphQL API (if available).
    """
    name: str
    display_name: str
    slug: str
    icon_url: str
    icon_asset_id: Optional[str] = None
    
    @classmethod
    def from_api_data(cls, hero_data: dict) -> "Hero":
        """
        Create a Hero from GraphQL API response data.
        
        Args:
            hero_data: Dictionary containing hero data from GraphQL API
            
        Returns:
            Hero instance with icon URL constructed from asset ID
        """
        name = hero_data.get("name", "")
        slug = hero_data.get("slug", "").lower() if hero_data.get("slug") else name.lower()
        data = hero_data.get("data", {})
        display_name = data.get("displayName", name)
        icon_asset_id = data.get("icon", "")
        
        # Construct icon URL from asset ID (correct pred.gg pattern)
        if icon_asset_id:
            icon_url = f"https://pred.gg/assets/{icon_asset_id}.png"
        else:
            # Fallback to slug-based URL if no asset ID (shouldn't happen)
            icon_url = f"https://pred.gg/heroes/{slug}.png"
        
        return cls(
            name=name,
            display_name=display_name,
            slug=slug,
            icon_url=icon_url,
            icon_asset_id=icon_asset_id if icon_asset_id else None
        )


class HeroRegistry:
    """
    Registry for hero data, allowing lookup by name or slug.
    
    This can be populated from the GraphQL API on startup.
    """
    
    def __init__(self) -> None:
        self._heroes_by_name: dict[str, Hero] = {}
        self._heroes_by_slug: dict[str, Hero] = {}
    
    def add_hero(self, hero: Hero) -> None:
        """Add a hero to the registry."""
        self._heroes_by_name[hero.name.lower()] = hero
        self._heroes_by_slug[hero.slug.lower()] = hero
    
    def get_by_name(self, name: str) -> Optional[Hero]:
        """Get a hero by name (case-insensitive)."""
        return self._heroes_by_name.get(name.lower())
    
    def get_by_slug(self, slug: str) -> Optional[Hero]:
        """Get a hero by slug (case-insensitive)."""
        return self._heroes_by_slug.get(slug.lower())
    
    def get_icon_url(self, hero_name: str) -> str:
        """
        Get icon URL for a hero by name.
        
        Falls back to constructing URL from hero name if not found in registry.
        Note: The fallback URL pattern may not work - registry should be populated
        from API for accurate URLs.
        
        Args:
            hero_name: The hero's name
            
        Returns:
            Icon URL for the hero
        """
        hero = self.get_by_name(hero_name)
        if hero:
            return hero.icon_url
        
        # Fallback: construct URL from hero name (lowercase)
        # This is a best-guess fallback and may not work
        slug = hero_name.lower()
        return f"https://pred.gg/heroes/{slug}.png"
    
    def get_all(self) -> list[Hero]:
        """Get all registered heroes."""
        return list(self._heroes_by_name.values())

