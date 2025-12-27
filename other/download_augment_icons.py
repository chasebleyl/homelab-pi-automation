#!/usr/bin/env python3
"""Download all augment/perk icons from the Predecessor API."""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import aiohttp
from predecessor_api import PredecessorAPI


ICONS_DIR = PROJECT_ROOT / "bots" / "belica-bot" / "icons" / "augments"
ASSET_BASE_URL = "https://pred.gg/assets"


async def fetch_all_perks(api: PredecessorAPI) -> list[dict]:
    """Fetch all perks with their data from the API."""
    query = """
    query GetAllPerks {
        perks {
            id
            name
            data {
                displayName
                name
                icon
                slot
                description
                hero {
                    name
                    slug
                }
            }
        }
    }
    """
    result = await api.query(query)
    return result.get("perks", [])


async def download_icon(session: aiohttp.ClientSession, icon_id: str, filepath: Path) -> bool:
    """Download a single icon."""
    url = f"{ASSET_BASE_URL}/{icon_id}.png"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                filepath.write_bytes(content)
                return True
            else:
                print(f"  Failed to download {url}: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False


def make_slug(name: str) -> str:
    """Convert name to slug format."""
    slug = name.lower().replace(" ", "-").replace("'", "").replace(".", "-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug


async def main():
    # Ensure output directory exists
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Downloading augment icons to: {ICONS_DIR}")
    print("=" * 60)

    api = PredecessorAPI("https://pred.gg/gql")

    try:
        # Fetch all perks
        print("\nFetching all perks from API...")
        perks = await fetch_all_perks(api)
        print(f"Found {len(perks)} perks\n")

        # Collect unique icons to download
        icons_to_download = {}  # icon_id -> (display_name, slot, hero_name)

        for perk in perks:
            perk_data = perk.get("data")
            if not perk_data:
                continue

            icon_id = perk_data.get("icon")
            if not icon_id:
                continue

            display_name = perk_data.get("displayName", perk.get("name", "Unknown"))
            slot = perk_data.get("slot", "UNKNOWN")
            hero = perk_data.get("hero")
            hero_name = hero.get("name") if hero else None

            # Create filename based on display name
            slug = make_slug(display_name)

            if icon_id not in icons_to_download:
                icons_to_download[icon_id] = (display_name, slug, slot, hero_name)

        print(f"Found {len(icons_to_download)} unique icons to download\n")

        # Group by slot type for display
        common_perks = []
        hero_perks = []

        for icon_id, (display_name, slug, slot, hero_name) in icons_to_download.items():
            if slot == "HERO_SPECIFIC_1":
                hero_perks.append((icon_id, display_name, slug, hero_name))
            else:
                common_perks.append((icon_id, display_name, slug, slot))

        print(f"Common augments: {len(common_perks)}")
        print(f"Hero-specific augments: {len(hero_perks)}")
        print()

        # Download icons
        async with aiohttp.ClientSession() as session:
            downloaded = 0
            skipped = 0
            failed = 0

            print("Downloading common augments...")
            for icon_id, display_name, slug, slot in sorted(common_perks, key=lambda x: x[1]):
                filepath = ICONS_DIR / f"{slug}.png"

                if filepath.exists():
                    print(f"  [SKIP] {display_name} ({slug}.png) - already exists")
                    skipped += 1
                    continue

                success = await download_icon(session, icon_id, filepath)
                if success:
                    print(f"  [OK] {display_name} -> {slug}.png")
                    downloaded += 1
                else:
                    failed += 1

            print("\nDownloading hero-specific augments...")
            for icon_id, display_name, slug, hero_name in sorted(hero_perks, key=lambda x: (x[3] or "", x[1])):
                filepath = ICONS_DIR / f"{slug}.png"

                if filepath.exists():
                    print(f"  [SKIP] {display_name} ({hero_name}) - already exists")
                    skipped += 1
                    continue

                success = await download_icon(session, icon_id, filepath)
                if success:
                    hero_label = f" ({hero_name})" if hero_name else ""
                    print(f"  [OK] {display_name}{hero_label} -> {slug}.png")
                    downloaded += 1
                else:
                    failed += 1

        print("\n" + "=" * 60)
        print(f"Download complete!")
        print(f"  Downloaded: {downloaded}")
        print(f"  Skipped (existing): {skipped}")
        print(f"  Failed: {failed}")
        print(f"  Total icons in folder: {len(list(ICONS_DIR.glob('*.png')))}")

    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(main())
