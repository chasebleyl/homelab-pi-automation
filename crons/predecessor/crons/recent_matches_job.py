"""Cron job for fetching and processing recent matches."""
import logging
from datetime import datetime, timedelta, timezone

from predecessor_api import PredecessorAPI
from data import (
    Database,
    ProcessedMatchRepository,
    SubscribedProfileRepository,
    PlayerMatchCursorRepository,
)
from services.match_fetcher import MatchFetcher
from services.bot_notifier import BotNotifier
from config import Config

logger = logging.getLogger("crons.recent_matches")

# Default lookback period when no cursor exists for a player
DEFAULT_LOOKBACK_HOURS = 24


def parse_end_time(end_time_str: str) -> datetime | None:
    """Parse an ISO format end time string to datetime."""
    if not end_time_str:
        return None
    try:
        # Handle both with and without timezone
        if end_time_str.endswith("Z"):
            end_time_str = end_time_str[:-1] + "+00:00"
        return datetime.fromisoformat(end_time_str)
    except ValueError:
        return None


async def recent_matches_job() -> None:
    """
    Cron job that fetches recent matches and processes them.

    This job uses cursor-based fetching:
    1. For each player, gets the last fetched match timestamp from DB
    2. If no cursor exists, looks back 24 hours
    3. Fetches matches from cursor time to now
    4. Updates cursor to latest match end time after processing
    """
    logger.info("Starting recent matches job")

    # Initialize services
    api = PredecessorAPI(
        api_url=Config.PRED_GG_API_URL,
        oauth_token_url=Config.PRED_GG_OAUTH_API_URL or None,
        client_id=Config.PRED_GG_CLIENT_ID or None,
        client_secret=Config.PRED_GG_CLIENT_SECRET or None,
    )
    db = Database()
    match_repo = ProcessedMatchRepository(db)
    profile_repo = SubscribedProfileRepository(db)
    cursor_repo = PlayerMatchCursorRepository(db)
    match_fetcher = MatchFetcher(api)
    bot_notifier = BotNotifier()

    try:
        # Connect to database
        await db.connect()

        # Get player UUIDs from subscribed profiles in database
        subscribed_profiles = await profile_repo.get_all_subscriptions()
        player_uuids_from_db = list(set(profile.player_uuid for profile in subscribed_profiles))

        # Also check environment variable for additional tracked players
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

        # Process each player individually with their own cursor
        total_processed = 0
        total_notified = 0
        now = datetime.now(timezone.utc)
        default_start = now - timedelta(hours=DEFAULT_LOOKBACK_HOURS)

        for player_uuid in all_player_uuids:
            # Get player's cursor (last fetched match time)
            last_match_time = await cursor_repo.get_last_match_time(player_uuid)

            if last_match_time:
                start_time = last_match_time
                logger.debug(f"Player {player_uuid}: cursor at {start_time}")
            else:
                start_time = default_start
                logger.debug(f"Player {player_uuid}: no cursor, using {DEFAULT_LOOKBACK_HOURS}h lookback")

            # Fetch matches for this player
            matches = await match_fetcher.fetch_matches_for_player(
                player_uuid=player_uuid,
                start_time=start_time,
                end_time=now
            )

            if not matches:
                logger.debug(f"Player {player_uuid}: no new matches")
                continue

            # Sort matches by end time ascending (oldest first) so Discord shows newest at bottom
            matches.sort(key=lambda m: m.get("endTime", ""))

            logger.info(f"Player {player_uuid}: found {len(matches)} matches")

            # Track the latest match end time for cursor update
            latest_end_time: datetime | None = None

            # Process each match (oldest to newest)
            for match_data in matches:
                match_uuid = match_data.get("uuid")
                if not match_uuid:
                    continue

                # Parse end time for cursor tracking
                end_time_str = match_data.get("endTime", "")
                match_end_time = parse_end_time(end_time_str)

                if match_end_time:
                    if latest_end_time is None or match_end_time > latest_end_time:
                        latest_end_time = match_end_time

                # Check if already processed
                if await match_repo.is_match_processed(match_uuid):
                    logger.debug(f"Match {match_uuid} already processed, skipping")
                    continue

                # Mark as processed
                match_id = match_data.get("id", match_uuid)
                await match_repo.mark_match_processed(match_uuid, match_id, end_time_str)
                total_processed += 1

                # Notify bot
                success = await bot_notifier.notify_match(match_data)
                if success:
                    await match_repo.mark_match_notified(match_uuid)
                    total_notified += 1

            # Update cursor to latest match end time
            if latest_end_time:
                await cursor_repo.update_cursor(player_uuid, latest_end_time)
                logger.debug(f"Player {player_uuid}: cursor updated to {latest_end_time}")

        logger.info(
            f"Recent matches job completed: "
            f"{total_processed} processed, {total_notified} notified"
        )

    except Exception as e:
        logger.error(f"Error in recent matches job: {e}", exc_info=True)

    finally:
        # Cleanup
        await bot_notifier.close()
        await db.close()
        await api.close()

