"""Script to download all item icons from the Predecessor GraphQL API.

Run from the monorepo root with the virtual environment activated:
    source .venv/bin/activate
    python bots/belica-bot/icons/items/download_item_icons.py

Or from the icons/items/ directory:
    cd bots/belica-bot/icons/items
    ../../../../.venv/bin/python download_item_icons.py
"""
import asyncio
import aiohttp
import sys
from pathlib import Path

# Add belica-bot to path for config module
SCRIPT_DIR = Path(__file__).parent
BELICA_BOT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(BELICA_BOT_ROOT))

from predecessor_api import PredecessorAPI, ItemService
from config import Config


async def download_image(session: aiohttp.ClientSession, url: str, filepath: Path) -> bool:
    """
    Download an image from a URL and save it to a file.

    Args:
        session: aiohttp session
        url: URL to download from
        filepath: Path to save the file to

    Returns:
        True if successful, False otherwise
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(content)
                return True
            else:
                print(f"  Failed to download {url}: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False


async def download_all_item_icons(output_dir: str = ".") -> None:
    """
    Download all item icons from the Predecessor API.

    Args:
        output_dir: Directory to save item icons to
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize API client and item service
    api = PredecessorAPI(Config.PRED_GG_API_URL)
    item_service = ItemService(api)

    print("Fetching items from GraphQL API...")
    try:
        items = await item_service.fetch_all_items()
        print(f"Found {len(items)} items")
    except Exception as e:
        print(f"Error fetching items: {e}")
        await api.close()
        return

    # Filter items that have icon data and are not hidden
    items_with_icons = [
        item for item in items
        if item.icon_asset_id and item.data and not item.data.is_hidden
    ]

    print(f"Found {len(items_with_icons)} visible items with icons")
    print(f"\nDownloading icons to '{output_dir}/' directory...\n")

    # Create aiohttp session for downloads
    async with aiohttp.ClientSession() as session:
        download_tasks = []

        for item in items_with_icons:
            item_name = item.name
            item_slug = item.slug
            display_name = item.data.display_name if item.data else item_name
            icon_url = item.icon_url

            # Use slug for filename (sanitize for filesystem)
            if item_slug:
                safe_name = "".join(c for c in item_slug if c.isalnum() or c in ('-', '_')).strip()
            else:
                safe_name = item_name.lower().replace(" ", "-")
                safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('-', '_')).strip()

            if not safe_name:
                safe_name = f"item_{item.id}"

            filename = f"{safe_name}.png"
            filepath = output_path / filename

            print(f"  {display_name} ({item_name})")
            print(f"   URL: {icon_url}")
            print(f"   Saving to: {filepath}")

            # Download the image
            task = download_image(session, icon_url, filepath)
            download_tasks.append((item_name, display_name, task))

        # Wait for all downloads to complete
        print("\n Downloading...\n")
        results = []
        for item_name, display_name, task in download_tasks:
            success = await task
            results.append((item_name, display_name, success))

    await api.close()

    # Print summary
    successful = sum(1 for _, _, success in results if success)
    failed = len(results) - successful

    print("\n" + "="*50)
    print("Download Summary")
    print("="*50)
    print(f"Successfully downloaded: {successful}")
    if failed > 0:
        print(f"Failed downloads: {failed}")
        print("\nFailed items:")
        for item_name, display_name, success in results:
            if not success:
                print(f"  - {display_name} ({item_name})")
    print(f"\nIcons saved to: {output_path.absolute()}")


async def main() -> None:
    """Main entry point."""
    # Get output directory from command line or use default (current directory)
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    await download_all_item_icons(output_dir)


if __name__ == "__main__":
    asyncio.run(main())
