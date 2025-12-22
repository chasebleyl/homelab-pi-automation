"""Configuration management for cron workers."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration container for cron workers."""
    
    # Predecessor API
    PRED_API_URL: str = os.getenv("PRED_API_URL", "https://pred.gg/gql")
    
    # Belica Bot HTTP endpoint
    BELICA_BOT_URL: str = os.getenv("BELICA_BOT_URL", "http://localhost:8080")
    
    # Cron job settings
    RECENT_MATCHES_CRON: str = os.getenv("RECENT_MATCHES_CRON", "*/5 * * * *")  # Every 5 minutes by default
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

