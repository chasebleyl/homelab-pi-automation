# Predecessor Data Layer

Shared data layer package for database and data entity management across all Predecessor projects.

**Stack:** asyncpg (raw SQL, no ORM), Alembic (migrations), testcontainers (testing)

## Overview

This package provides:
- Database connection management (PostgreSQL via asyncpg)
- Data entities and models (dataclasses)
- Repository pattern for data access
- Schema migrations (Alembic)

## Installation

Install as an editable package:

```bash
cd data
pip install -e .
```

Or from other projects:
```bash
pip install -e ../data
```

## Usage

### Database Connection

```python
from data import Database, DatabaseConfig

# Initialize database
db = Database()
await db.connect()

# Use the connection pool
async with db.pool.acquire() as conn:
    result = await conn.fetch("SELECT * FROM processed_matches")

# Close when done
await db.close()
```

### Repository Pattern

#### Processed Matches

```python
from data import Database, ProcessedMatchRepository

db = Database()
await db.connect()

repo = ProcessedMatchRepository(db)

# Check if match is processed
is_processed = await repo.is_match_processed("match-uuid")

# Mark match as processed
await repo.mark_match_processed("match-uuid", "match-id", "2024-01-01T00:00:00Z")

# Mark as notified
await repo.mark_match_notified("match-uuid")
```

#### Subscribed Profiles

```python
from data import Database, SubscribedProfileRepository

db = Database()
await db.connect()

repo = SubscribedProfileRepository(db)

# Add a profile subscription
await repo.add_profile(guild_id=123456789, player_uuid="player-uuid")

# Get all subscriptions for a guild
profiles = await repo.get_profiles(guild_id=123456789)

# Check if subscribed
is_subscribed = await repo.is_subscribed(guild_id=123456789, player_uuid="player-uuid")

# Remove subscription
await repo.remove_profile(guild_id=123456789, player_uuid="player-uuid")
```

#### Target Channels

```python
from data import Database, TargetChannelRepository

db = Database()
await db.connect()

repo = TargetChannelRepository(db)

# Add a target channel
await repo.add_channel(guild_id=123456789, channel_id=987654321)

# Get all target channels for a guild
channels = await repo.get_channels(guild_id=123456789)

# Check if channel is configured
is_target = await repo.is_target_channel(guild_id=123456789, channel_id=987654321)

# Remove channel
await repo.remove_channel(guild_id=123456789, channel_id=987654321)

# Get all target channels across all guilds
all_channels = await repo.get_all_target_channels()
```

## Configuration

Set environment variables:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/predecessor
# OR
DB_HOST=localhost
DB_PORT=5432
DB_NAME=predecessor
DB_USER=postgres
DB_PASSWORD=your_password
```

## Migrations

Schema is managed via Alembic. **Migrations must be run manually** before starting the app.

```bash
# Apply all migrations
cd data && alembic upgrade head

# Check current version
cd data && alembic current

# Create new migration
cd data && alembic revision -m "description"
```

Migrations are **not** auto-applied on connect. This is intentional for production safety.

## Schema

Tables managed by migrations:

- `processed_matches` - Tracks processed matches with UUID, ID, end time, and notification status
- `subscribed_profiles` - Tracks Discord guild subscriptions to player profiles (guild_id, player_uuid, subscribed_at)
- `target_channels` - Tracks Discord channels configured to receive match notifications (guild_id, channel_id, configured_at)

