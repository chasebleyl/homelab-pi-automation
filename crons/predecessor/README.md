# Predecessor API Cron Workers

Cron workers for fetching and processing Predecessor match data from the GraphQL API.

## Overview

This service runs scheduled jobs (cron) that:
1. Fetch recent match data from the Predecessor GraphQL API
2. Process and deduplicate matches using PostgreSQL
3. Send match notifications to belica-bot via HTTP

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Access to the Predecessor GraphQL API

### Installation

1. Install dependencies:
```bash
cd predecessor-api-crons
pip install -r requirements.txt
```

This will automatically install:
- All Python dependencies (APScheduler, aiohttp, etc.)
- The shared `predecessor-api-client` package in editable mode
- The shared `data` package in editable mode

2. Set up environment variables (create a `.env` file):
```bash
# Predecessor API
PRED_API_URL=https://pred.gg/gql

# PostgreSQL Database (used by data package)
DATABASE_URL=postgresql://user:password@localhost:5432/predecessor
# OR use individual parameters:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=predecessor
# DB_USER=postgres
# DB_PASSWORD=your_password

# Belica Bot HTTP endpoint
BELICA_BOT_URL=http://localhost:8080

# Cron job settings
RECENT_MATCHES_CRON=*/5 * * * *  # Every 5 minutes (cron format)
RECENT_MATCHES_INTERVAL_MINUTES=10  # Look back 10 minutes
```

3. Create the PostgreSQL database:
```bash
createdb predecessor
```

The schema will be automatically created on first run.

### Configuration

#### Player UUIDs

The cron worker needs to know which players to query for matches. Currently, the API doesn't support querying "all recent matches" directly, so we query by player UUIDs.

The cron workers automatically track players that have been subscribed via Discord bot commands. These subscriptions are stored in the `subscribed_profiles` database table.

You can also configure additional player UUIDs via environment variable (useful for testing or manual tracking):

```bash
TRACKED_PLAYER_UUIDS=uuid1,uuid2,uuid3
```

**Note**: Player UUIDs from both sources (database subscriptions and environment variable) are combined and deduplicated.

### Running

Start the cron worker:
```bash
python main.py
```

The worker will:
- Connect to PostgreSQL
- Start the scheduler
- Run jobs according to the configured cron schedule

## Jobs

### Recent Matches Job

Fetches matches from the last N minutes (configurable) for tracked players.

**Schedule**: Configured via `RECENT_MATCHES_CRON` (default: every 5 minutes)

**Process**:
1. Queries the GraphQL API for matches from tracked players
2. Filters matches within the time interval
3. Checks PostgreSQL to see which matches have already been processed
4. Sends new matches to belica-bot via HTTP POST
5. Marks matches as processed in the database

## API Endpoints

The cron workers send HTTP POST requests to belica-bot:

**POST /api/matches**
- Body: Match data from GraphQL API (JSON)
- Response: `{"status": "success", "match_uuid": "..."}`

## Database Schema

The service creates a `processed_matches` table:

```sql
CREATE TABLE processed_matches (
    match_uuid TEXT PRIMARY KEY,
    match_id TEXT NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    notified_bot BOOLEAN NOT NULL DEFAULT FALSE
);
```

## Development

### Adding New Jobs

1. Create a new job function in `crons/`:
```python
async def my_new_job() -> None:
    # Job logic here
    pass
```

2. Register it in `main.py`:
```python
self.scheduler.add_job(
    my_new_job,
    trigger=CronTrigger(...),
    id="my_new_job",
    name="My New Job"
)
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL or DB_* environment variables
- Ensure the database exists

### No Matches Found
- Verify tracked player UUIDs are configured
- Check that players have played matches in the time interval
- Review API logs for errors

### Bot Notifications Failing
- Verify belica-bot HTTP server is running
- Check BELICA_BOT_URL is correct
- Review bot logs for errors

