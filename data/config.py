"""Database configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from monorepo root (parent of data/)
_root_env = Path(__file__).parent.parent / ".env"
load_dotenv(_root_env)


class DatabaseConfig:
    """Configuration container for database connections.

    Can be used as a class (reads from environment at call time) or
    instantiated with a specific database URL for testing.
    """

    def __init__(self, database_url: str | None = None) -> None:
        """Initialize config with optional explicit database URL.

        Args:
            database_url: If provided, use this URL instead of environment variables.
        """
        self._database_url = database_url

    def get_database_url(self) -> str:
        """Get the database connection URL."""
        # If explicit URL was provided, use it
        if self._database_url:
            return self._database_url

        # Otherwise read from environment (at call time, not import time)
        env_url = os.getenv("DATABASE_URL", "")
        if env_url:
            return env_url

        # Construct from individual parameters
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "predecessor")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    def validate(self) -> None:
        """Validate that required configuration is present."""
        db_url = self.get_database_url()
        if not db_url or db_url == "postgresql://postgres:@localhost:5432/predecessor":
            raise ValueError("DATABASE_URL or DB_* environment variables must be set")

