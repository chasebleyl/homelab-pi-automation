"""Script to fetch all items from Predecessor API and save to JSON."""
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Add predecessor-api-client to path
sys.path.insert(0, str(Path(__file__).parent / "predecessor-api-client"))

from predecessor_api import PredecessorAPI, ItemService, Item, ItemData, ItemStat, ItemEffect


def item_to_dict(item: Item) -> dict[str, Any]:
    """Convert an Item object to a dictionary for JSON serialization."""
    result = {
        "id": item.id,
        "name": item.name,
        "slug": item.slug,
        "icon_url": item.icon_url,
        "icon_asset_id": item.icon_asset_id,
    }
    
    if item.data:
        result["data"] = item_data_to_dict(item.data)
    
    return result


def item_data_to_dict(item_data: ItemData) -> dict[str, Any]:
    """Convert an ItemData object to a dictionary for JSON serialization."""
    return {
        "id": item_data.id,
        "name": item_data.name,
        "display_name": item_data.display_name,
        "icon": item_data.icon,
        "small_icon": item_data.small_icon,
        "price": item_data.price,
        "total_price": item_data.total_price,
        "game_id": item_data.game_id,
        "aggression_type": item_data.aggression_type.value,
        "class": item_data.class_type.value,
        "rarity": item_data.rarity.value,
        "slot_type": item_data.slot_type.value,
        "is_evolved": item_data.is_evolved,
        "is_hidden": item_data.is_hidden,
        "stats": [item_stat_to_dict(stat) for stat in item_data.stats],
        "effects": [item_effect_to_dict(effect) for effect in item_data.effects],
        "builds_from_ids": item_data.builds_from_ids,
        "builds_into_ids": item_data.builds_into_ids,
        "blocks_ids": item_data.blocks_ids,
        "blocked_by_ids": item_data.blocked_by_ids,
    }


def item_stat_to_dict(stat: ItemStat) -> dict[str, Any]:
    """Convert an ItemStat object to a dictionary for JSON serialization."""
    return {
        "id": stat.id,
        "stat": stat.stat.value,
        "value": stat.value,
        "show_percent": stat.show_percent,
    }


def item_effect_to_dict(effect: ItemEffect) -> dict[str, Any]:
    """Convert an ItemEffect object to a dictionary for JSON serialization."""
    return {
        "id": effect.id,
        "name": effect.name,
        "text": effect.text,
        "active": effect.active,
        "condition": effect.condition,
        "cooldown": effect.cooldown,
    }


async def fetch_all_items():
    """Fetch all items from the API and save to JSON file."""
    # Initialize API client
    api = PredecessorAPI("https://pred.gg/gql")
    item_service = ItemService(api)
    
    try:
        print("Fetching all items from Predecessor API...")
        items = await item_service.fetch_all_items()
        
        print(f"Fetched {len(items)} items")
        
        # Convert items to dictionaries
        items_dict = [item_to_dict(item) for item in items]
        
        # Save to JSON file
        output_file = Path(__file__).parent / "items.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(items_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(items_dict)} items to {output_file}")
        
        # Print some statistics
        items_with_data = sum(1 for item in items if item.data)
        print(f"Items with data: {items_with_data}")
        print(f"Items without data: {len(items) - items_with_data}")
        
        if items:
            # Show a sample item
            sample_item = items[0]
            print(f"\nSample item:")
            print(f"  ID: {sample_item.id}")
            print(f"  Name: {sample_item.name}")
            print(f"  Slug: {sample_item.slug}")
            if sample_item.data:
                print(f"  Display Name: {sample_item.data.display_name}")
                print(f"  Price: {sample_item.data.price}")
                print(f"  Rarity: {sample_item.data.rarity.value}")
                print(f"  Slot Type: {sample_item.data.slot_type.value}")
        
    except Exception as e:
        print(f"Error fetching items: {e}")
        raise
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(fetch_all_items())

