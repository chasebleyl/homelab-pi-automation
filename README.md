# homelab-pi-automation

Monorepo for homelab services running on Raspberry Pi, with shared PostgreSQL infrastructure.

## Current Services

### Predecessor (Discord Bot)
Match tracking bot for the [Predecessor](https://www.yourpredecessor.com/) game.

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # Edit with your tokens

# Database
docker compose up -d postgres
cd data && alembic upgrade head && cd ..

# Run
python bots/belica-bot/bot.py
```

## Packages

| Package | Description |
|---------|-------------|
| [data](data/) | Shared PostgreSQL data layer |
| [ansible](ansible/) | Raspberry Pi deployment |
| [bots/belica-bot](bots/belica-bot/) | Predecessor Discord bot |
| [api/predecessor](api/predecessor/) | Predecessor GraphQL API client |
| [crons/predecessor](crons/predecessor/) | Predecessor match fetching jobs |

## Documentation

- [CLAUDE.md](CLAUDE.md) - Architecture, environment variables, testing
- [ansible/CLAUDE.md](ansible/CLAUDE.md) - Deployment commands and roles
