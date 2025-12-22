"""
Pytest fixtures for database testing using testcontainers.

Usage:
    Tests that need a database can use the `db` fixture:

    async def test_something(db):
        # db is a connected Database instance
        repo = SomeRepository(db)
        await repo.do_something()

    For tests that need raw connection string:

    async def test_raw_connection(postgres_url):
        # postgres_url is the connection string
        conn = await asyncpg.connect(postgres_url)
        ...
"""

import os
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    """
    Spin up a PostgreSQL container for the test session.

    The container is started once and reused for all tests in the session.
    """
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def postgres_url(postgres_container) -> str:
    """
    Get the PostgreSQL connection URL from the container.

    Returns asyncpg-compatible URL (postgresql:// scheme).
    """
    # testcontainers returns psycopg2-style URL, convert to asyncpg format
    url = postgres_container.get_connection_url()
    # Replace driver prefix for asyncpg compatibility
    if url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql://")
    return url


@pytest.fixture(scope="session")
def set_database_env(postgres_url):
    """
    Set DATABASE_URL environment variable for the test session.

    Useful when code reads from environment variables.
    """
    original = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = postgres_url
    yield postgres_url
    if original is not None:
        os.environ["DATABASE_URL"] = original
    else:
        os.environ.pop("DATABASE_URL", None)


@pytest.fixture
async def db(postgres_url):
    """
    Provide a connected Database instance with schema initialized.

    Each test gets a fresh transaction that is rolled back after the test,
    keeping the database clean between tests.
    """
    from data import Database, DatabaseConfig

    # Create config with explicit test database URL
    config = DatabaseConfig(database_url=postgres_url)
    database = Database(config=config)
    # run_migrations=True uses _init_schema() for quick test setup
    # Production uses: cd data && alembic upgrade head
    await database.connect(run_migrations=True)

    yield database

    await database.close()


@pytest.fixture
async def db_with_clean_tables(db):
    """
    Provide a Database instance with all tables truncated.

    Use this when you need a completely clean database state.
    """
    async with db.pool.acquire() as conn:
        # Truncate all tables (add more as needed)
        await conn.execute("""
            TRUNCATE TABLE
                processed_matches,
                subscribed_profiles,
                target_channels
            CASCADE
        """)

    yield db
