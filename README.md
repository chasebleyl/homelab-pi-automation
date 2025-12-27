# cb-discord-bots

Monorepo for [Predecessor](https://www.yourpredecessor.com/) game Discord bots and supporting services.

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # Edit with your Discord token

# Database
docker compose up -d postgres
cd data && alembic upgrade head && cd ..

# Run
python bots/belica-bot/bot.py
```

## Packages

| Package | Description |
|---------|-------------|
| [bots/belica-bot](bots/belica-bot/) | Discord bot for match tracking |
| [api/predecessor](api/predecessor/) | Shared GraphQL API client |
| [crons/predecessor](crons/predecessor/) | Scheduled match fetching jobs |
| [data](data/) | Shared PostgreSQL data layer |
| [ansible](ansible/) | Raspberry Pi deployment |

## Documentation

- [CLAUDE.md](CLAUDE.md) - Architecture, environment variables, testing
- [ansible/CLAUDE.md](ansible/CLAUDE.md) - Deployment commands and roles
