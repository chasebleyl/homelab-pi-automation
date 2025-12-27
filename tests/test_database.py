"""
Example tests demonstrating testcontainers PostgreSQL usage.

Run with: pytest tests/test_database.py -v
"""

import pytest


async def test_database_connection(db):
    """Test that we can connect to the test database."""
    async with db.pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
        assert result == 1


async def test_schema_tables_exist(db):
    """Test that schema initialization creates expected tables."""
    async with db.pool.acquire() as conn:
        # Check that our tables exist in the predecessor schema
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'predecessor'
            ORDER BY table_name
        """)
        table_names = [row["table_name"] for row in tables]

        assert "processed_matches" in table_names
        assert "subscribed_profiles" in table_names
        assert "target_channels" in table_names


async def test_repository_insert_and_query(db):
    """Test basic repository operations."""
    from data import SubscribedProfileRepository

    repo = SubscribedProfileRepository(db)

    # Subscribe a test player
    guild_id = 123456789
    player_uuid = "test-player-uuid"

    result = await repo.add_profile(guild_id, player_uuid)
    assert result is True  # Should return True for new subscription

    # Verify subscription exists
    profiles = await repo.get_profiles(guild_id)
    assert len(profiles) == 1
    assert profiles[0] == player_uuid

    # Verify is_subscribed works
    assert await repo.is_subscribed(guild_id, player_uuid) is True


async def test_clean_tables_fixture(db_with_clean_tables):
    """Test that db_with_clean_tables provides empty tables."""
    async with db_with_clean_tables.pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM subscribed_profiles")
        assert count == 0
