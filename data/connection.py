"""Database connection management."""
import asyncpg
import logging
from typing import Optional

from .config import DatabaseConfig

logger = logging.getLogger("data.connection")


class Database:
    """PostgreSQL database connection manager."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None) -> None:
        """
        Initialize the database connection manager.
        
        Args:
            config: Optional DatabaseConfig instance. If None, uses default config.
        """
        self.config = config or DatabaseConfig()
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self, run_migrations: bool = False) -> None:
        """Create the database connection pool.

        Args:
            run_migrations: If True, run schema initialization (for testing only).
                           Production should use: alembic upgrade head
        """
        if self._pool is None:
            # Parse DATABASE_URL or use individual parameters
            db_url = self.config.get_database_url()
            schema = self.config.get_schema()

            # asyncpg uses postgres:// but we might have postgresql:// from Config
            # Convert postgresql:// to postgres:// if needed
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgres://", 1)

            # Set search_path via server_settings so it persists across connection reuse
            # Note: Using init= callback doesn't work because asyncpg resets connection
            # state when returning connections to the pool
            self._pool = await asyncpg.create_pool(
                db_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                server_settings={"search_path": f"{schema}, public"}
            )
            logger.info(f"Database connection pool created (schema: {schema})")

            # Schema initialization - only for testing
            # Production uses: cd data && alembic upgrade head
            if run_migrations:
                await self._init_schema()
    
    async def _init_schema(self) -> None:
        """Initialize database schema (create tables if they don't exist)."""
        schema = self.config.get_schema()
        async with self._pool.acquire() as conn:
            # Create schema if it doesn't exist
            await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_matches (
                    match_uuid TEXT PRIMARY KEY,
                    match_id TEXT NOT NULL,
                    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    processed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    notified_bot BOOLEAN NOT NULL DEFAULT FALSE
                );
                
                CREATE INDEX IF NOT EXISTS idx_processed_matches_end_time 
                    ON processed_matches(end_time);
                
                CREATE INDEX IF NOT EXISTS idx_processed_matches_processed_at 
                    ON processed_matches(processed_at);
                
                CREATE TABLE IF NOT EXISTS subscribed_profiles (
                    guild_id BIGINT NOT NULL,
                    player_uuid TEXT NOT NULL,
                    player_name TEXT,
                    subscribed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (guild_id, player_uuid)
                );
                
                CREATE INDEX IF NOT EXISTS idx_subscribed_profiles_guild_id 
                    ON subscribed_profiles(guild_id);
                
                CREATE INDEX IF NOT EXISTS idx_subscribed_profiles_player_uuid 
                    ON subscribed_profiles(player_uuid);
                
                CREATE TABLE IF NOT EXISTS target_channels (
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    configured_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (guild_id, channel_id)
                );

                CREATE INDEX IF NOT EXISTS idx_target_channels_guild_id
                    ON target_channels(guild_id);

                CREATE TABLE IF NOT EXISTS player_match_cursors (
                    player_uuid TEXT PRIMARY KEY,
                    last_match_end_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_player_match_cursors_last_match_end_time
                    ON player_match_cursors(last_match_end_time);
            """)
            logger.info("Database schema initialized")
    
    async def close(self) -> None:
        """Close the database connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")
    
    @property
    def pool(self) -> asyncpg.Pool:
        """Get the connection pool."""
        if self._pool is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._pool

