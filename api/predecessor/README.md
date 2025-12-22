# Predecessor API Client

Python client library for the Predecessor GraphQL API.

## Installation

For local development in a monorepo:

```bash
# From the predecessor-api-client directory
pip install -e .

# Or from the belica-bot directory
pip install -e ../predecessor-api-client
```

## Usage

### Basic API Client

```python
from predecessor_api import PredecessorAPI

# Initialize the API client
api = PredecessorAPI("https://api.pred.gg/graphql")

# Execute a GraphQL query
result = await api.query("""
    query {
        heroes {
            name
        }
    }
""")

# Don't forget to close the session
await api.close()
```

### Hero Service

```python
from predecessor_api import PredecessorAPI, HeroService, HeroRegistry

api = PredecessorAPI("https://api.pred.gg/graphql")
hero_service = HeroService(api)

# Fetch all heroes
heroes = await hero_service.fetch_all_heroes()

# Populate a registry
registry = HeroRegistry()
await hero_service.populate_hero_registry(registry)

# Lookup by name
hero = registry.get_by_name("Countess")

await api.close()
```

### Item Service

```python
from predecessor_api import PredecessorAPI, ItemService, ItemRegistry

api = PredecessorAPI("https://api.pred.gg/graphql")
item_service = ItemService(api)

# Fetch all items
items = await item_service.fetch_all_items()

# Fetch a specific item by ID
item = await item_service.fetch_item_by_id("item-id-here")

# Fetch a specific item by slug
item = await item_service.fetch_item_by_slug("item-slug-here")

# Fetch using convenience method (by ID or slug)
item = await item_service.fetch_item(item_id="item-id-here")
# or
item = await item_service.fetch_item(item_slug="item-slug-here")

# Populate a registry
registry = ItemRegistry()
await item_service.populate_item_registry(registry)

# Lookup by name, slug, or ID
item = registry.get_by_name("Item Name")
item = registry.get_by_slug("item-slug")
item = registry.get_by_id("item-id")

await api.close()
```

