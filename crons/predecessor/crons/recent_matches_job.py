"""Cron job for fetching and processing recent matches."""
import logging

from predecessor_api import PredecessorAPI
from data import Database, ProcessedMatchRepository, SubscribedProfileRepository
from services.match_fetcher import MatchFetcher
from services.bot_notifier import BotNotifier
from config import Config

logger = logging.getLogger("crons.recent_matches")


async def recent_matches_job() -> None:
    """
    Cron job that fetches recent matches and processes them.
    
    This job:
    1. Fetches matches from the last N minutes (configurable)
    2. Checks which matches haven't been processed yet
    3. Sends new matches to belica-bot for notification
    """
    logger.info("Starting recent matches job")
    
    # Initialize services
    api = PredecessorAPI(Config.PRED_API_URL)
    db = Database()
    match_repo = ProcessedMatchRepository(db)
    profile_repo = SubscribedProfileRepository(db)
    match_fetcher = MatchFetcher(api)
    bot_notifier = BotNotifier()
    
    try:
        # Connect to database
        await db.connect()
        
        # Get player UUIDs from subscribed profiles in database
        # This allows the cron workers to automatically track players
        # that users have subscribed to via Discord bot commands
        subscribed_profiles = await profile_repo.get_all_subscriptions()
        player_uuids_from_db = list(set(profile.player_uuid for profile in subscribed_profiles))
        
        # Also check environment variable for additional tracked players
        # (useful for testing or manual tracking)
        player_uuids_from_env = Config.get_tracked_player_uuids()
        
        # Combine and deduplicate
        all_player_uuids = list(set(player_uuids_from_db + player_uuids_from_env))
        
        if not all_player_uuids:
            logger.warning(
                "No tracked player UUIDs found. "
                "Subscribe to player profiles via Discord bot commands, or "
                "set TRACKED_PLAYER_UUIDS environment variable with comma-separated UUIDs."
            )
            return
        
        logger.info(
            f"Fetching matches for {len(all_player_uuids)} tracked player(s) "
            f"({len(player_uuids_from_db)} from subscriptions, {len(player_uuids_from_env)} from config)"
        )
        
        matches = await match_fetcher.fetch_recent_matches_by_interval(
            interval_minutes=Config.RECENT_MATCHES_INTERVAL_MINUTES,
            player_uuids=all_player_uuids
        )
        
        logger.info(f"Found {len(matches)} matches in the time interval")
        
        # Process each match
        processed_count = 0
        notified_count = 0
        
        for match_data in matches:
            match_uuid = match_data.get("uuid")
            if not match_uuid:
                continue
            
            # Check if already processed
            if await match_repo.is_match_processed(match_uuid):
                logger.debug(f"Match {match_uuid} already processed, skipping")
                continue
            
            # Mark as processed
            match_id = match_data.get("id", match_uuid)
            end_time_str = match_data.get("endTime", "")
            await match_repo.mark_match_processed(match_uuid, match_id, end_time_str)
            processed_count += 1
            
            # Notify bot
            success = await bot_notifier.notify_match(match_data)
            if success:
                await match_repo.mark_match_notified(match_uuid)
                notified_count += 1
        
        logger.info(
            f"Recent matches job completed: "
            f"{processed_count} processed, {notified_count} notified"
        )
    
    except Exception as e:
        logger.error(f"Error in recent matches job: {e}", exc_info=True)
    
    finally:
        # Cleanup
        await bot_notifier.close()
        await db.close()
        await api.close()

