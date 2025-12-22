"""Bot configuration management."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration container for the bot."""
    
    # Discord
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    TEST_GUILD_ID: str = os.getenv("TEST_GUILD_ID", "")  # Optional: for faster command syncing during development
    
    # Predecessor API
    PRED_API_URL: str = os.getenv("PRED_API_URL", "https://pred.gg/gql")
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN environment variable is required")

