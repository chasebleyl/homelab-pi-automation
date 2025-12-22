# cb-discord-bots

Monorepo for Predecessor game Discord bots and supporting services. Uses the pred.gg GraphQL API.

## Packages

| Package | Description | CLAUDE.md |
|---------|-------------|-----------|
| `bots/belica-bot/` | Discord bot (discord.py) | [Details](bots/belica-bot/CLAUDE.md) |
| `api/predecessor/` | Shared GraphQL API client library | [Details](api/predecessor/CLAUDE.md) |
| `crons/predecessor/` | Scheduled jobs for match fetching | [Details](crons/predecessor/CLAUDE.md) |
| `data/` | Shared PostgreSQL data layer | [Details](data/CLAUDE.md) |

## Quick Start

```bash
# Create virtual environment at monorepo root
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies (including dev/test dependencies)
pip install -e ".[dev]"

# Run the Discord bot
python bots/belica-bot/bot.py

# Run cron workers
python crons/predecessor/main.py

# Run tests
pytest
```

## Architecture Overview

```
Discord Users
     │
     ▼
[belica-bot] ◄──HTTP POST──┐
     │                      │
     │                      │
     ▼                      │
[PostgreSQL] ◄────────[predecessor-api-crons]
     │                      │
     └──────────────────────┴──────► [pred.gg API]
```

1. Users subscribe to player profiles via bot slash commands
2. Cron workers poll pred.gg API for matches of subscribed players
3. New matches are POSTed to belica-bot HTTP endpoint
4. Bot formats and posts results to configured Discord channels

## Development Setup

The monorepo uses a single virtual environment at the root:

```bash
# One-time setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

All sub-packages (`api/predecessor`, `data`) are automatically available via the root `pyproject.toml` package mappings.

## Testing

Tests use **testcontainers** to spin up a real PostgreSQL database in Docker:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_database.py -v
```

**Requirements:** Docker must be running for database tests.

### Writing Tests

```python
# tests/test_example.py

async def test_with_database(db):
    """db fixture provides a connected Database instance."""
    from data import SomeRepository
    repo = SomeRepository(db)
    result = await repo.do_something()
    assert result is not None

async def test_with_clean_database(db_with_clean_tables):
    """db_with_clean_tables truncates all tables before the test."""
    # Tables are guaranteed empty
    ...
```

Available fixtures (see `tests/conftest.py`):
- `postgres_container` - Raw testcontainer instance (session-scoped)
- `postgres_url` - Connection URL string (session-scoped)
- `db` - Connected `Database` instance with schema initialized
- `db_with_clean_tables` - Same as `db` but with all tables truncated

## Python Version

Python 3.9+ required
