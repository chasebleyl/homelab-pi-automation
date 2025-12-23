"""Test script to generate a leaderboard image from cached fixture."""
import json
import sys
from pathlib import Path

# Add paths for imports
SCRIPT_DIR = Path(__file__).parent
BELICA_BOT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(BELICA_BOT_ROOT))

from services.leaderboard_image import generate_leaderboard_image


def main():
    # Load cached fixture
    fixture_path = BELICA_BOT_ROOT / "fixtures" / "detailed_match.json"

    if not fixture_path.exists():
        print(f"Error: Fixture not found at {fixture_path}")
        print("Run fetch_detailed_match.py first to cache match data.")
        return

    with open(fixture_path) as f:
        match_data = json.load(f)

    print(f"Loaded match: {match_data['match']['uuid']}")
    print(f"Duration: {match_data['match']['duration']}s")
    print(f"Players: {len(match_data['match']['matchPlayers'])}")

    # Generate image
    print("\nGenerating leaderboard image...")
    image_bytes = generate_leaderboard_image(match_data)

    # Save to file
    output_path = BELICA_BOT_ROOT / "test_leaderboard.png"
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"Saved to: {output_path}")
    print(f"Size: {len(image_bytes):,} bytes")


if __name__ == "__main__":
    main()
