"""Script to download all hero icons from the Predecessor GraphQL API."""
import asyncio
import aiohttp
import os
from pathlib import Path
from typing import Optional

from predecessor_api import PredecessorAPI, HeroService
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
                print(f"  ❌ Failed to download {url}: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"  ❌ Error downloading {url}: {e}")
        return False


async def download_all_hero_icons(output_dir: str = "hero_icons") -> None:
    """
    Download all hero icons from the Predecessor API.
    
    Args:
        output_dir: Directory to save hero icons to
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize API client and hero service
    api = PredecessorAPI(Config.PRED_GG_API_URL)
    hero_service = HeroService(api)
    
    print("Fetching heroes from GraphQL API...")
    try:
        heroes = await hero_service.fetch_all_heroes()
        print(f"Found {len(heroes)} heroes")
    except Exception as e:
        print(f"❌ Error fetching heroes: {e}")
        await api.close()
        return
    
    # Filter heroes that have icon data
    heroes_with_icons = [hero for hero in heroes if hero.icon_asset_id]
    
    print(f"Found {len(heroes_with_icons)} heroes with icons")
    print(f"\nDownloading icons to '{output_dir}/' directory...\n")
    
    # Create aiohttp session for downloads
    async with aiohttp.ClientSession() as session:
        download_tasks = []
        
        for hero in heroes_with_icons:
            hero_name = hero.name
            hero_slug = hero.slug
            display_name = hero.display_name
            icon_url = hero.icon_url
            
            # Use slug for filename (sanitize for filesystem)
            safe_name = "".join(c for c in hero_slug if c.isalnum() or c in ('-', '_')).strip()
            if not safe_name:
                safe_name = hero_name.lower().replace(" ", "_")
            
            filename = f"{safe_name}.png"
            filepath = output_path / filename
            
            print(f"📥 {display_name} ({hero_name})")
            print(f"   URL: {icon_url}")
            print(f"   Saving to: {filepath}")
            
            # Download the image
            task = download_image(session, icon_url, filepath)
            download_tasks.append((hero_name, display_name, task))
        
        # Wait for all downloads to complete
        print("\n⏳ Downloading...\n")
        results = []
        for hero_name, display_name, task in download_tasks:
            success = await task
            results.append((hero_name, display_name, success))
    
    await api.close()
    
    # Print summary
    successful = sum(1 for _, _, success in results if success)
    failed = len(results) - successful
    
    print("\n" + "="*50)
    print("Download Summary")
    print("="*50)
    print(f"✅ Successfully downloaded: {successful}")
    if failed > 0:
        print(f"❌ Failed downloads: {failed}")
        print("\nFailed heroes:")
        for hero_name, display_name, success in results:
            if not success:
                print(f"  - {display_name} ({hero_name})")
    print(f"\n📁 Icons saved to: {output_path.absolute()}")
    print("\n💡 You can now upload these PNGs as custom emojis to your Discord server!")


async def main() -> None:
    """Main entry point."""
    import sys
    
    # Get output directory from command line or use default
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "hero_icons"
    
    await download_all_hero_icons(output_dir)


if __name__ == "__main__":
    asyncio.run(main())

