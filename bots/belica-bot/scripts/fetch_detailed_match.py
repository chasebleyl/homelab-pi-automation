"""Fetch detailed match data and cache it for development."""
import asyncio
import json
import sys
from pathlib import Path

# Add paths for imports
SCRIPT_DIR = Path(__file__).parent
BELICA_BOT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(BELICA_BOT_ROOT))

from predecessor_api import PredecessorAPI, MatchService
from config import Config


async def fetch_and_cache_match(match_id: str, output_path: Path) -> dict:
    """Fetch detailed match data and save to JSON file."""
    api = PredecessorAPI(Config.PRED_GG_API_URL)
    match_service = MatchService(api)

    print(f"Fetching match: {match_id}")

    try:
        result = await match_service.fetch_detailed_match(match_id)

        if not result:
            print("Error: Match not found")
            await api.close()
            return None

        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"Cached to: {output_path}")
        print(f"Match duration: {result['match']['duration']}s")
        print(f"Players: {len(result['match']['matchPlayers'])}")

        await api.close()
        return result

    except Exception as e:
        print(f"Error: {e}")
        await api.close()
        raise


async def main():
    match_id = sys.argv[1] if len(sys.argv) > 1 else "02163d3a-a24c-428a-8008-d23bd59f6c09"
    output_path = BELICA_BOT_ROOT / "fixtures" / "detailed_match.json"

    await fetch_and_cache_match(match_id, output_path)


if __name__ == "__main__":
    asyncio.run(main())
