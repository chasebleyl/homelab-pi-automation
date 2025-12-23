# cb-discord-bots

Monorepo for [Predecessor](https://www.yourpredecessor.com/) game Discord bots and supporting services.

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your Discord token

# Start database
docker compose up -d postgres

# Run migrations
cd data && alembic upgrade head && cd ..

# Run the bot
python bots/belica-bot/bot.py
```

## Packages

| Package | Description |
|---------|-------------|
| [bots/belica-bot](bots/belica-bot/) | Discord bot for match tracking |
| [api/predecessor](api/predecessor/) | Shared GraphQL API client |
| [crons/predecessor](crons/predecessor/) | Scheduled match fetching jobs |
| [data](data/) | Shared PostgreSQL data layer |

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed architecture, environment variables, and development docs.
