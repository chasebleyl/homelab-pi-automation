# crons/predecessor

Scheduled cron workers for fetching Predecessor match data and notifying the Discord bot.

## Quick Start

```bash
# From monorepo root
pip install -e ".[dev]"
python crons/predecessor/main.py
```

## Structure

```
crons/predecessor/
├── main.py                    # Entry point - CronWorker with APScheduler
├── config.py                  # Environment variable configuration
├── crons/
│   └── recent_matches_job.py  # Main job: fetch matches for subscribed players
└── services/
    ├── match_fetcher.py       # Fetches matches from API
    └── bot_notifier.py        # POSTs matches to belica-bot
```

## Architecture

- **CronWorker**: APScheduler-based scheduler that runs jobs on configured intervals
- **Jobs**: Async functions in `crons/` that perform scheduled work
- **Services**: Helper classes for API calls and bot communication

## Data Flow

1. Job queries database for subscribed player UUIDs
2. Fetches recent matches from pred.gg API for those players
3. Checks `processed_matches` table to skip already-handled matches
4. POSTs new matches to belica-bot HTTP endpoint (`/api/matches`)
5. Marks matches as processed and notified

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PRED_API_URL` | No | https://pred.gg/gql | Predecessor GraphQL API URL |
| `BELICA_BOT_URL` | No | http://localhost:8080 | Bot HTTP endpoint |
| `RECENT_MATCHES_CRON` | No | */5 * * * * | Cron schedule (every 5 min) |
| `RECENT_MATCHES_INTERVAL_MINUTES` | No | 10 | Look-back window for matches |
| `TRACKED_PLAYER_UUIDS` | No | - | Comma-separated UUIDs (in addition to DB subscriptions) |
| `DATABASE_URL` | No* | - | PostgreSQL connection URL |
| `DB_HOST` | No* | localhost | Database host |
| `DB_PORT` | No* | 5432 | Database port |
| `DB_NAME` | No* | predecessor | Database name |
| `DB_USER` | No* | postgres | Database user |
| `DB_PASSWORD` | No* | - | Database password |

*Either `DATABASE_URL` or `DB_*` variables required.

## Dependencies

All dependencies managed in root `pyproject.toml`. Shared packages auto-available:
- `predecessor_api`: API client and services
- `data`: Database connection and repositories

## Key Patterns

### Adding a New Cron Job

1. Create job function in `crons/`:
```python
# crons/my_job.py
async def my_job() -> None:
    logger.info("Running my job")
    # ... job logic
```

2. Register in `main.py`:
```python
from crons.my_job import my_job

# In CronWorker.setup_jobs():
self.scheduler.add_job(
    my_job,
    trigger=CronTrigger(minute="*/10"),
    id="my_job",
    name="My Job Description"
)
```

### Bot Notification Format
```python
# POST to /api/matches
{
    "uuid": "match-uuid",
    "id": "match-id",
    "endTime": "2024-01-01T12:00:00Z",
    "players": [...]
}
```
