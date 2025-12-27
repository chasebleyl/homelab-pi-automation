# homelab-pi-automation

Monorepo for homelab services running on Raspberry Pi, with shared PostgreSQL infrastructure.

## Packages

| Package | Description | CLAUDE.md |
|---------|-------------|-----------|
| `data/` | Shared PostgreSQL data layer | [Details](data/CLAUDE.md) |
| `ansible/` | Raspberry Pi deployment automation | [Details](ansible/CLAUDE.md) |
| `bots/belica-bot/` | Predecessor Discord bot (discord.py) | [Details](bots/belica-bot/CLAUDE.md) |
| `api/predecessor/` | Predecessor GraphQL API client | [Details](api/predecessor/CLAUDE.md) |
| `crons/predecessor/` | Predecessor match fetching jobs | [Details](crons/predecessor/CLAUDE.md) |

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

### Predecessor Service

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

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Discord token, etc.

# Start PostgreSQL
docker compose up -d postgres
```

All sub-packages (`api/predecessor`, `data`) are automatically available via the root `pyproject.toml` package mappings.

## Environment Variables

Single `.env` file at the monorepo root (see `.env.example`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | - | Discord bot token |
| `TEST_GUILD_ID` | No | - | Guild ID for fast slash command sync |
| `PRED_GG_API_URL` | No | https://pred.gg/gql | Predecessor GraphQL API URL |
| `DB_PASSWORD` | Yes* | - | Database password |
| `DB_HOST` | No | localhost | Database host |
| `DB_PORT` | No | 5432 | Database port |
| `DB_NAME` | No | hobbydata | Database name |
| `DB_USER` | No | postgres | Database user |
| `DATABASE_URL` | No* | - | Full PostgreSQL URL (alternative to DB_* vars) |
| `BELICA_BOT_URL` | No | http://localhost:8080 | Bot HTTP endpoint (for crons) |

*Either `DATABASE_URL` or `DB_PASSWORD` required for database features.

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
