# api/predecessor

Shared GraphQL API client library for the Predecessor game API (pred.gg).

## Installation

```bash
# From monorepo root (recommended)
pip install -e ".[dev]"

# Package is auto-available as predecessor_api
```

## Structure

```
api/predecessor/
├── __init__.py               # Package exports (import as predecessor_api)
├── client.py                 # PredecessorAPI - GraphQL client
├── models.py                 # Hero, HeroRegistry
├── item_models.py            # Item, ItemRegistry, ItemData, etc.
├── match_models.py           # MatchData, MatchPlayerData, enums
├── hero_service.py           # HeroService - hero data fetching
├── item_service.py           # ItemService - item data fetching
├── match_service.py          # MatchService - match data fetching
└── player_matches_service.py # PlayerMatchesService - player match history
```

## Usage

### Basic Client Usage
```python
from predecessor_api import PredecessorAPI

api = PredecessorAPI("https://pred.gg/gql")
data = await api.query("""
    query {
        heroes { id name }
    }
""")
await api.close()
```

### Using Services
```python
from predecessor_api import (
    PredecessorAPI,
    HeroService,
    HeroRegistry,
    ItemService,
    ItemRegistry,
    PlayerMatchesService
)

api = PredecessorAPI("https://pred.gg/gql")

# Hero data
hero_service = HeroService(api)
hero_registry = HeroRegistry()
await hero_service.populate_hero_registry(hero_registry)
hero = hero_registry.get_by_name("Murdock")

# Item data
item_service = ItemService(api)
item_registry = ItemRegistry()
await item_service.populate_item_registry(item_registry)
item = item_registry.get_by_name("Deathstalker")

# Player matches
player_service = PlayerMatchesService(api)
matches = await player_service.get_recent_matches(player_uuid, limit=10)

await api.close()
```

## Key Classes

### PredecessorAPI
Async GraphQL client with session management.
- `query(query_str, variables)` - Execute GraphQL query
- `close()` - Clean up HTTP session

### Registries
In-memory caches for game data:
- `HeroRegistry` - Heroes indexed by ID and name
- `ItemRegistry` - Items indexed by ID and name

### Services
Fetch and parse API data:
- `HeroService.populate_hero_registry(registry)`
- `ItemService.populate_item_registry(registry)`
- `MatchService.get_match_by_uuid(uuid)`
- `PlayerMatchesService.get_recent_matches(player_uuid, limit)`

### Models
Data classes for game entities:
- `Hero(id, name, display_name, ...)`
- `Item(id, name, ...)`
- `MatchData(uuid, id, end_time, players, ...)`
- `MatchPlayerData(player_uuid, hero_id, kills, deaths, assists, ...)`

## Adding New Functionality

1. Add models to appropriate `*_models.py` file
2. Add service methods to appropriate `*_service.py` file
3. Export from `__init__.py`
