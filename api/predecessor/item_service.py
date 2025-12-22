"""Service for fetching item data from the Predecessor GraphQL API."""
from typing import Optional
from .client import PredecessorAPI
from .item_models import Item, ItemRegistry, ItemData


class ItemService:
    """Service for fetching and managing item data from the Predecessor API."""
    
    # GraphQL query for fetching all items
    GET_ALL_ITEMS_QUERY = """
    query GetAllItems {
        items {
            id
            name
            slug
            data {
                id
                name
                displayName
                icon
                smallIcon
                price
                totalPrice
                gameId
                aggressionType
                class
                rarity
                slotType
                isEvolved
                isHidden
                stats {
                    id
                    stat
                    value
                    showPercent
                }
                effects {
                    id
                    name
                    text
                    active
                    condition
                    cooldown
                }
                buildsFrom {
                    id
                }
                buildsInto {
                    id
                }
                blocks {
                    id
                }
                blockedBy {
                    id
                }
            }
        }
    }
    """
    
    # GraphQL query for fetching a specific item by ID
    GET_ITEM_BY_ID_QUERY = """
    query GetItemById($itemId: ID!) {
        item(by: { id: $itemId }) {
            id
            name
            slug
            data {
                id
                name
                displayName
                icon
                smallIcon
                price
                totalPrice
                gameId
                aggressionType
                class
                rarity
                slotType
                isEvolved
                isHidden
                stats {
                    id
                    stat
                    value
                    showPercent
                }
                effects {
                    id
                    name
                    text
                    active
                    condition
                    cooldown
                }
                buildsFrom {
                    id
                }
                buildsInto {
                    id
                }
                blocks {
                    id
                }
                blockedBy {
                    id
                }
            }
        }
    }
    """
    
    # GraphQL query for fetching a specific item by slug
    GET_ITEM_BY_SLUG_QUERY = """
    query GetItemBySlug($itemSlug: String!) {
        item(by: { slug: $itemSlug }) {
            id
            name
            slug
            data {
                id
                name
                displayName
                icon
                smallIcon
                price
                totalPrice
                gameId
                aggressionType
                class
                rarity
                slotType
                isEvolved
                isHidden
                stats {
                    id
                    stat
                    value
                    showPercent
                }
                effects {
                    id
                    name
                    text
                    active
                    condition
                    cooldown
                }
                buildsFrom {
                    id
                }
                buildsInto {
                    id
                }
                blocks {
                    id
                }
                blockedBy {
                    id
                }
            }
        }
    }
    """
    
    def __init__(self, api: PredecessorAPI) -> None:
        """
        Initialize the item service.
        
        Args:
            api: PredecessorAPI client instance
        """
        self.api = api
    
    async def fetch_all_items(self) -> list[Item]:
        """
        Fetch all items from the API.
        
        Returns:
            List of Item instances
        """
        result = await self.api.query(self.GET_ALL_ITEMS_QUERY)
        items_data = result.get("items", [])
        
        items = []
        for item_data in items_data:
            if item_data:
                item = Item.from_api_data(item_data)
                items.append(item)
        
        return items
    
    async def fetch_item_by_id(self, item_id: str) -> Optional[Item]:
        """
        Fetch a specific item by ID.
        
        Args:
            item_id: The item's unique identifier
            
        Returns:
            Item instance if found, None otherwise
        """
        result = await self.api.query(
            self.GET_ITEM_BY_ID_QUERY,
            variables={"itemId": item_id}
        )
        
        item_data = result.get("item")
        if not item_data:
            return None
        
        return Item.from_api_data(item_data)
    
    async def fetch_item_by_slug(self, item_slug: str) -> Optional[Item]:
        """
        Fetch a specific item by slug.
        
        Args:
            item_slug: The item's URL slug
            
        Returns:
            Item instance if found, None otherwise
        """
        result = await self.api.query(
            self.GET_ITEM_BY_SLUG_QUERY,
            variables={"itemSlug": item_slug}
        )
        
        item_data = result.get("item")
        if not item_data:
            return None
        
        return Item.from_api_data(item_data)
    
    async def fetch_item(self, item_id: Optional[str] = None, item_slug: Optional[str] = None) -> Optional[Item]:
        """
        Fetch a specific item by ID or slug.
        
        Args:
            item_id: The item's unique identifier (optional)
            item_slug: The item's URL slug (optional)
            
        Returns:
            Item instance if found, None otherwise
            
        Raises:
            ValueError: If neither item_id nor item_slug is provided
        """
        if item_id:
            return await self.fetch_item_by_id(item_id)
        elif item_slug:
            return await self.fetch_item_by_slug(item_slug)
        else:
            raise ValueError("Either item_id or item_slug must be provided")
    
    async def populate_item_registry(self, registry: ItemRegistry) -> None:
        """
        Populate the item registry by querying all items from the GraphQL API.
        
        Args:
            registry: ItemRegistry to populate
        """
        try:
            items = await self.fetch_all_items()
            for item in items:
                registry.add_item(item)
        except Exception as e:
            # Log error but don't fail - registry will use fallback URLs
            print(f"Warning: Failed to populate item registry: {e}")

