"""Configuration management for cron workers."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from monorepo root
_root_env = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_root_env)


class Config:
    """Configuration container for cron workers."""

    # Predecessor API
    PRED_GG_API_URL: str = os.getenv("PRED_GG_API_URL", "https://pred.gg/gql")
    PRED_GG_OAUTH_API_URL: str = os.getenv("PRED_GG_OAUTH_API_URL", "")
    PRED_GG_CLIENT_ID: str = os.getenv("PRED_GG_CLIENT_ID", "")
    PRED_GG_CLIENT_SECRET: str = os.getenv("PRED_GG_CLIENT_SECRET", "")

    # Belica Bot HTTP endpoint
    BELICA_BOT_URL: str = os.getenv("BELICA_BOT_URL", "http://localhost:8080")
    
    # Cron job settings
    RECENT_MATCHES_CRON: str = os.getenv("RECENT_MATCHES_CRON", "* * * * *")  # Every 1 minute by default
    RECENT_MATCHES_INTERVAL_MINUTES: int = int(os.getenv("RECENT_MATCHES_INTERVAL_MINUTES", "10"))  # Look back 10 minutes
    
    # Tracked player UUIDs (comma-separated)
    TRACKED_PLAYER_UUIDS: str = os.getenv("TRACKED_PLAYER_UUIDS", "")
    
    @classmethod
    def get_tracked_player_uuids(cls) -> list[str]:
        """Get list of tracked player UUIDs from environment."""
        if not cls.TRACKED_PLAYER_UUIDS:
            return []
        return [uuid.strip() for uuid in cls.TRACKED_PLAYER_UUIDS.split(",") if uuid.strip()]
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        # Database validation is now handled by the data package
        pass

