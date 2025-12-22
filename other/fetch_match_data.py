"""Script to fetch match data from Predecessor API and save to JSON."""
import asyncio
import json
import sys
from pathlib import Path

# Add predecessor-api-client to path
sys.path.insert(0, str(Path(__file__).parent / "predecessor-api-client"))

from predecessor_api import PredecessorAPI

# Match ID to fetch
MATCH_ID = "75a755dd-9594-476a-96fc-2f78dfbe8e2d"

# Start with minimal query - just match basics
# We'll build this up incrementally
MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
    }
}
"""


async def fetch_match_data():
    """Fetch match data and save to JSON file."""
    # Initialize API client
    api = PredecessorAPI("https://pred.gg/gql")
    
    try:
        print(f"Step 1: Testing basic match query for ID: {MATCH_ID}")
        
        # Execute the minimal query
        variables = {
            "matchKey": {
                "id": MATCH_ID
            }
        }
        
        result = await api.query(MATCH_QUERY, variables)
        
        # Check if match was found
        if not result.get("match"):
            print("Error: Match not found!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return
        
        print(f"✓ Match found: {result['match']['id']} (UUID: {result['match']['uuid']})")
        
        # Now build up the query incrementally
        print("\nStep 2: Adding match metadata...")
        await build_query_incrementally(api, variables)
        
    except Exception as e:
        print(f"Error fetching match data: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await api.close()


async def build_query_incrementally(api: PredecessorAPI, variables: dict):
    """Build up the query incrementally, testing each addition."""
    global MATCH_QUERY
    
    # Step 2: Add match metadata
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print("✓ Match metadata added successfully")
    else:
        print("✗ Failed to add match metadata")
        return
    
    # Step 3: Add version
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
        version {
            id
            name
            build
            changelist
            releaseDate
        }
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print("✓ Version info added successfully")
    else:
        print("✗ Failed to add version info")
        return
    
    # Step 4: Add basic matchPlayers
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
        version {
            id
            name
            build
            changelist
            releaseDate
        }
        matchPlayers {
            id
            name
            team
            role
            level
            kills
            deaths
            assists
            gold
        }
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print(f"✓ Basic matchPlayers added successfully ({len(result['match']['matchPlayers'])} players)")
    else:
        print("✗ Failed to add basic matchPlayers")
        return
    
    # Step 5: Add player info
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
        version {
            id
            name
            build
            changelist
            releaseDate
        }
        matchPlayers {
            id
            name
            team
            role
            level
            kills
            deaths
            assists
            gold
            player {
                id
                uuid
                name
            }
        }
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print("✓ Player info added successfully")
    else:
        print("✗ Failed to add player info")
        return
    
    # Step 6: Add hero info
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
        version {
            id
            name
            build
            changelist
            releaseDate
        }
        matchPlayers {
            id
            name
            team
            role
            level
            kills
            deaths
            assists
            gold
            player {
                id
                uuid
                name
            }
            hero {
                id
                name
                slug
            }
            heroData {
                id
                name
                displayName
                icon
                classes
                roles
                mainAttributes {
                    attackPower
                    abilityPower
                    durability
                    mobility
                }
            }
        }
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print("✓ Hero info added successfully")
    else:
        print("✗ Failed to add hero info")
        return
    
    # Step 7: Add more player stats
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
        version {
            id
            name
            build
            changelist
            releaseDate
        }
        matchPlayers {
            id
            name
            team
            role
            level
            kills
            deaths
            assists
            gold
            minionsKilled
            heroDamage
            heroDamageTaken
            totalDamageDealt
            totalDamageDealtToObjectives
            totalDamageDealtToStructures
            totalDamageTaken
            totalDamageMitigated
            totalHealingDone
            largestKillingSpree
            largestCriticalStrike
            multiKill
            wardsPlaced
            wardsDestroyed
            endTime
            player {
                id
                uuid
                name
            }
            hero {
                id
                name
                slug
            }
            heroData {
                id
                name
                displayName
                icon
                classes
                roles
                mainAttributes {
                    attackPower
                    abilityPower
                    durability
                    mobility
                }
            }
        }
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print("✓ Additional player stats added successfully")
    else:
        print("✗ Failed to add additional player stats")
        return
    
    # Step 8: Add inventory items with stats
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
        version {
            id
            name
            build
            changelist
            releaseDate
        }
        matchPlayers {
            id
            name
            team
            role
            level
            kills
            deaths
            assists
            gold
            minionsKilled
            heroDamage
            heroDamageTaken
            totalDamageDealt
            totalDamageDealtToObjectives
            totalDamageDealtToStructures
            totalDamageTaken
            totalDamageMitigated
            totalHealingDone
            largestKillingSpree
            largestCriticalStrike
            multiKill
            wardsPlaced
            wardsDestroyed
            endTime
            player {
                id
                uuid
                name
            }
            hero {
                id
                name
                slug
            }
            heroData {
                id
                name
                displayName
                icon
                classes
                roles
                mainAttributes {
                    attackPower
                    abilityPower
                    durability
                    mobility
                }
            }
            inventoryItemData {
                id
                name
                displayName
                icon
                smallIcon
                gameId
                price
                totalPrice
                rarity
                slotType
                class
                aggressionType
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
            }
        }
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print("✓ Inventory items with stats added successfully")
    else:
        print("✗ Failed to add inventory items")
        return
    
    # Step 9: Add perk data
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
        version {
            id
            name
            build
            changelist
            releaseDate
        }
        matchPlayers {
            id
            name
            team
            role
            level
            kills
            deaths
            assists
            gold
            minionsKilled
            heroDamage
            heroDamageTaken
            totalDamageDealt
            totalDamageDealtToObjectives
            totalDamageDealtToStructures
            totalDamageTaken
            totalDamageMitigated
            totalHealingDone
            largestKillingSpree
            largestCriticalStrike
            multiKill
            wardsPlaced
            wardsDestroyed
            endTime
            player {
                id
                uuid
                name
            }
            hero {
                id
                name
                slug
            }
            heroData {
                id
                name
                displayName
                icon
                classes
                roles
                mainAttributes {
                    attackPower
                    abilityPower
                    durability
                    mobility
                }
            }
            inventoryItemData {
                id
                name
                displayName
                icon
                smallIcon
                gameId
                price
                totalPrice
                rarity
                slotType
                class
                aggressionType
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
            }
            perkData {
                id
                name
                displayName
                icon
                description
                simpleDescription
                slot
                displayOrder
                aggressionTypes
            }
        }
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print("✓ Perk data added successfully")
    else:
        print("✗ Failed to add perk data")
        return
    
    # Step 10: Add transactions (item purchase timestamps)
    MATCH_QUERY = """
query GetMatch($matchKey: MatchKey!) {
    match(by: $matchKey) {
        id
        uuid
        duration
        endReason
        endTime
        startTime
        gameMode
        region
        winningTeam
        version {
            id
            name
            build
            changelist
            releaseDate
        }
        matchPlayers {
            id
            name
            team
            role
            level
            kills
            deaths
            assists
            gold
            minionsKilled
            heroDamage
            heroDamageTaken
            totalDamageDealt
            totalDamageDealtToObjectives
            totalDamageDealtToStructures
            totalDamageTaken
            totalDamageMitigated
            totalHealingDone
            largestKillingSpree
            largestCriticalStrike
            multiKill
            wardsPlaced
            wardsDestroyed
            endTime
            player {
                id
                uuid
                name
            }
            hero {
                id
                name
                slug
            }
            heroData {
                id
                name
                displayName
                icon
                classes
                roles
                mainAttributes {
                    attackPower
                    abilityPower
                    durability
                    mobility
                }
            }
            inventoryItemData {
                id
                name
                displayName
                icon
                smallIcon
                gameId
                price
                totalPrice
                rarity
                slotType
                class
                aggressionType
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
            }
            perkData {
                id
                name
                displayName
                icon
                description
                simpleDescription
                slot
                displayOrder
                aggressionTypes
            }
            transactions {
                gameTime
                transactionType
                itemData {
                    id
                    name
                    displayName
                    icon
                    smallIcon
                    gameId
                    price
                    totalPrice
                    rarity
                    slotType
                    class
                    aggressionType
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
                }
            }
        }
    }
}
"""
    result = await api.query(MATCH_QUERY, variables)
    if result.get("match"):
        print("✓ Transactions data added successfully")
    else:
        print("✗ Failed to add transactions data")
        return
    
    # Step 11: Filter to only offlane players
    print("✓ Filtering to offlane players only...")
    if result.get("match") and result["match"].get("matchPlayers"):
        original_count = len(result["match"]["matchPlayers"])
        result["match"]["matchPlayers"] = [
            mp for mp in result["match"]["matchPlayers"]
            if mp.get("role") == "OFFLANE"
        ]
        filtered_count = len(result["match"]["matchPlayers"])
        print(f"  Filtered from {original_count} players to {filtered_count} offlane players")
    
    # Final: Save the complete result
    output_file = f"match_{MATCH_ID}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Complete match data saved to {output_file}")
    print(f"  Match ID: {result['match']['id']}")
    print(f"  Offlane Players: {len(result['match']['matchPlayers'])}")
    
    # Print summary of items and transactions per player
    for mp in result['match']['matchPlayers']:
        hero_name = mp.get('heroData', {}).get('displayName', 'Unknown')
        item_count = len(mp.get('inventoryItemData', []))
        transaction_count = len(mp.get('transactions', []))
        buy_count = sum(1 for t in mp.get('transactions', []) if t.get('transactionType') == 'BUY')
        print(f"  - {hero_name}: {item_count} items, {transaction_count} transactions ({buy_count} purchases)")


if __name__ == "__main__":
    asyncio.run(fetch_match_data())

