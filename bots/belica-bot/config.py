"""Bot configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from monorepo root
_root_env = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_root_env)


class Config:
    """Configuration container for the bot."""

    # Discord
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    TEST_GUILD_ID: str = os.getenv("TEST_GUILD_ID", "")  # Optional: for faster command syncing during development

    # Predecessor API
    PRED_GG_API_URL: str = os.getenv("PRED_GG_API_URL", "https://pred.gg/gql")
    PRED_GG_OAUTH_API_URL: str = os.getenv("PRED_GG_OAUTH_API_URL", "")
    PRED_GG_CLIENT_ID: str = os.getenv("PRED_GG_CLIENT_ID", "")
    PRED_GG_CLIENT_SECRET: str = os.getenv("PRED_GG_CLIENT_SECRET", "")
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN environment variable is required")

