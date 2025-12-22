# data

Shared PostgreSQL data layer for the monorepo. Provides database connection, entities, and repositories.

**Stack:** asyncpg (raw SQL, no ORM), Alembic (migrations), testcontainers (testing)

## Installation

```bash
# From monorepo root (recommended)
pip install -e ".[dev]"

# Package is auto-available as data
```

## Structure

```
data/
├── __init__.py       # Package exports
├── config.py         # DatabaseConfig - environment variable handling
├── connection.py     # Database - connection pool management
├── predecessor.py    # Predecessor entities: ProcessedMatch
├── belica_bot.py     # Bot entities: SubscribedProfile, TargetChannel
├── repositories.py   # CRUD operations for each entity
├── alembic.ini       # Alembic configuration
└── migrations/       # Database migrations
    ├── env.py        # Alembic environment config
    ├── script.py.mako # Migration template
    └── versions/     # Migration files
```

## Usage

```python
from data import (
    Database,
    ProcessedMatchRepository,
    SubscribedProfileRepository,
    TargetChannelRepository
)

# Connect
db = Database()
await db.connect()

# Use repositories
match_repo = ProcessedMatchRepository(db)
profile_repo = SubscribedProfileRepository(db)
channel_repo = TargetChannelRepository(db)

# Query
is_processed = await match_repo.is_match_processed("match-uuid")
subscriptions = await profile_repo.get_subscriptions_for_guild(guild_id)
channels = await channel_repo.get_channels_for_guild(guild_id)

# Cleanup
await db.close()
```

## Entities

### ProcessedMatch
Tracks which matches have been fetched and notified.
```python
@dataclass
class ProcessedMatch:
    match_uuid: str       # Primary key
    match_id: str
    end_time: datetime
    processed_at: datetime
    notified_bot: bool
```

### SubscribedProfile
Discord guild subscriptions to player profiles.
```python
@dataclass
class SubscribedProfile:
    guild_id: int         # Composite PK
    player_uuid: str      # Composite PK
    subscribed_at: datetime
```

### TargetChannel
Discord channels configured to receive match notifications.
```python
@dataclass
class TargetChannel:
    guild_id: int         # Composite PK
    channel_id: int       # Composite PK
    configured_at: datetime
```

## Database Schema

Tables managed via Alembic migrations:
- `processed_matches` - Match processing state
- `subscribed_profiles` - Guild player subscriptions
- `target_channels` - Guild notification channels

## Migrations

Uses Alembic for database migrations. All commands run from the `data/` directory.

### Run migrations (production)
```bash
cd data
alembic upgrade head
```

### Check current migration status
```bash
cd data
alembic current
```

### Create a new migration
```bash
cd data
alembic revision -m "add player_name column"
# Edit the generated file in migrations/versions/
```

### Rollback one migration
```bash
cd data
alembic downgrade -1
```

### View migration history
```bash
cd data
alembic history
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No* | - | Full PostgreSQL URL |
| `DB_HOST` | No* | localhost | Database host |
| `DB_PORT` | No* | 5432 | Database port |
| `DB_NAME` | No* | predecessor | Database name |
| `DB_USER` | No* | postgres | Database user |
| `DB_PASSWORD` | No* | - | Database password |

*Either `DATABASE_URL` or the individual `DB_*` variables must be set.

## Key Patterns

### Adding a New Entity

1. Add dataclass to appropriate entity file (`predecessor.py` or `belica_bot.py`):
```python
@dataclass
class MyEntity:
    id: str
    # ... fields

    @classmethod
    def from_row(cls, row: dict) -> "MyEntity":
        return cls(id=row["id"], ...)
```

2. Add repository to `repositories.py`:
```python
class MyEntityRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_by_id(self, id: str) -> Optional[MyEntity]:
        async with self._db.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM my_table WHERE id = $1", id)
            return MyEntity.from_row(dict(row)) if row else None
```

3. Create a migration for the new table:
```bash
cd data
alembic revision -m "add my_table"
```

4. Edit the migration file with your SQL:
```python
def upgrade() -> None:
    op.execute("""
        CREATE TABLE my_table (
            id TEXT PRIMARY KEY,
            ...
        )
    """)

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS my_table")
```

5. Also add to `connection.py` `_init_schema()` for test compatibility:
```python
CREATE TABLE IF NOT EXISTS my_table (...);
```

6. Export from `__init__.py`
