"""Service for managing hero registry from GraphQL API."""
from typing import Optional
from models.hero import Hero, HeroRegistry
from api import PredecessorAPI


async def populate_hero_registry(api: PredecessorAPI, registry: HeroRegistry) -> None:
    """
    Populate the hero registry by querying all heroes from the GraphQL API.
    
    Args:
        api: PredecessorAPI client instance
        registry: HeroRegistry to populate
    """
    query = """
    query GetAllHeroes {
        heroes {
            id
            name
            slug
            data {
                icon
                displayName
            }
        }
    }
    """
    
    try:
        result = await api.query(query)
        heroes_data = result.get("heroes", [])
        
        for hero_data in heroes_data:
            if hero_data and hero_data.get("data"):
                hero = Hero.from_api_data(hero_data)
                registry.add_hero(hero)
    except Exception as e:
        # Log error but don't fail - registry will use fallback URLs
        print(f"Warning: Failed to populate hero registry: {e}")


def get_hero_registry() -> HeroRegistry:
    """
    Get a singleton hero registry instance.
    
    Note: This should be populated on bot startup using populate_hero_registry().
    """
    if not hasattr(get_hero_registry, "_instance"):
        get_hero_registry._instance = HeroRegistry()
    return get_hero_registry._instance

