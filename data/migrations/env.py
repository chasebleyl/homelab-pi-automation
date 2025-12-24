"""Alembic migration environment configuration."""
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool, text

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DatabaseConfig

# Alembic Config object
config = context.config

# Setup logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# No SQLAlchemy models - we use raw SQL migrations
target_metadata = None

# Database configuration
db_config = DatabaseConfig()


def get_url() -> str:
    """Get database URL from environment."""
    return db_config.get_database_url()


def get_schema() -> str:
    """Get database schema from environment."""
    return db_config.get_schema()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This generates SQL scripts without connecting to the database.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # alembic_version table stays in public schema (default)
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and connects to the database.
    """
    schema = get_schema()
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Set search_path so tables are created in the app schema
        # Note: schema may not exist yet (migration 000 creates it)
        # PostgreSQL ignores non-existent schemas in search_path
        connection.execute(text(f"SET search_path TO {schema}, public"))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # alembic_version table stays in public schema (default)
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
