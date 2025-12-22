"""Service for fetching hero data from the Predecessor GraphQL API."""
from typing import Optional
from .client import PredecessorAPI
from .models import Hero, HeroRegistry


class HeroService:
    """Service for fetching and managing hero data from the Predecessor API."""
    
    # GraphQL query for fetching all heroes
    GET_ALL_HEROES_QUERY = """
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
    
    def __init__(self, api: PredecessorAPI) -> None:
        """
        Initialize the hero service.
        
        Args:
            api: PredecessorAPI client instance
        """
        self.api = api
    
    async def fetch_all_heroes(self) -> list[Hero]:
        """
        Fetch all heroes from the API.
        
        Returns:
            List of Hero instances
        """
        result = await self.api.query(self.GET_ALL_HEROES_QUERY)
        heroes_data = result.get("heroes", [])
        
        heroes = []
        for hero_data in heroes_data:
            if hero_data and hero_data.get("data"):
                hero = Hero.from_api_data(hero_data)
                heroes.append(hero)
        
        return heroes
    
    async def populate_hero_registry(self, registry: HeroRegistry) -> None:
        """
        Populate the hero registry by querying all heroes from the GraphQL API.
        
        Args:
            registry: HeroRegistry to populate
        """
        try:
            heroes = await self.fetch_all_heroes()
            for hero in heroes:
                registry.add_hero(hero)
        except Exception as e:
            # Log error but don't fail - registry will use fallback URLs
            print(f"Warning: Failed to populate hero registry: {e}")






