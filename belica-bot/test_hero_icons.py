"""Test script to query hero icons from the GraphQL API and verify URLs."""
import asyncio
import sys
import aiohttp
from api import PredecessorAPI
from config import Config
from models.hero import Hero, HeroRegistry
from services.hero_registry import populate_hero_registry


async def test_url_exists(url: str) -> bool:
    """Check if a URL exists (returns 200)."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status == 200
    except:
        return False


async def test_asset_id_urls(asset_id: str) -> list[tuple[str, bool]]:
    """Test different URL patterns for asset IDs."""
    patterns = [
        f"https://cdn.pred.gg/{asset_id}.png",
        f"https://assets.pred.gg/{asset_id}.png",
        f"https://pred.gg/cdn/{asset_id}.png",
        f"https://pred.gg/assets/{asset_id}.png",
        f"https://pred.gg/images/heroes/{asset_id}.png",
        f"https://api.pred.gg/assets/{asset_id}.png",
    ]
    
    results = []
    for url in patterns:
        exists = await test_url_exists(url)
        results.append((url, exists))
        if exists:
            break  # Found working pattern, stop testing
    
    return results


async def test_hero_icons() -> None:
    """Query heroes and their icon URLs from the API."""
    api = PredecessorAPI(Config.PRED_API_URL)
    registry = HeroRegistry()
    
    try:
        print("Querying heroes from GraphQL API...")
        await populate_hero_registry(api, registry)
        
        heroes = registry.get_all()
        print(f"\nFound {len(heroes)} heroes in registry\n")
        
        # Test first hero's asset ID to find working URL pattern
        if heroes:
            test_hero = heroes[0]
            if test_hero.icon_asset_id:
                print(f"Testing asset ID URL patterns for {test_hero.name} (asset_id: {test_hero.icon_asset_id}):")
                asset_results = await test_asset_id_urls(test_hero.icon_asset_id)
                for url, exists in asset_results:
                    status = "✓ WORKS!" if exists else "✗"
                    print(f"  {url:60} | {status}")
                    if exists:
                        print(f"\n  Found working pattern! Using: {url.split('/')[-2]}/{{asset_id}}.png\n")
                        break
        
        print("=" * 80)
        print("Testing ALL hero icon URLs:")
        print("-" * 80)
        
        working_count = 0
        missing_asset_id_count = 0
        failed_count = 0
        
        # Sort heroes by name for consistent output
        sorted_heroes = sorted(heroes, key=lambda h: h.name)
        
        for hero in sorted_heroes:
            if not hero.icon_asset_id:
                status = "⚠ NO ASSET ID"
                missing_asset_id_count += 1
            else:
                url_exists = await test_url_exists(hero.icon_url)
                if url_exists:
                    status = "✓"
                    working_count += 1
                else:
                    status = "✗ FAILED"
                    failed_count += 1
            
            print(f"{hero.name:20} | {hero.icon_url:60} | {status}")
        
        print("\n" + "=" * 80)
        print("Summary:")
        print(f"  Total heroes: {len(heroes)}")
        print(f"  Working URLs: {working_count}")
        print(f"  Failed URLs: {failed_count}")
        print(f"  Missing asset IDs: {missing_asset_id_count}")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error querying API: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        await api.close()


if __name__ == "__main__":
    Config.validate()
    asyncio.run(test_hero_icons())

