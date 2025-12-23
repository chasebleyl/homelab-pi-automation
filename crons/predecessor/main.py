"""Main entry point for cron workers."""
import asyncio
import logging
import signal
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from data import DatabaseConfig
from crons.recent_matches_job import recent_matches_job

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("crons.main")


class CronWorker:
    """Main cron worker scheduler."""
    
    def __init__(self) -> None:
        """Initialize the cron worker."""
        self.scheduler = AsyncIOScheduler()
        self.running = False
    
    def setup_jobs(self) -> None:
        """Set up all cron jobs."""
        # Parse cron expression (e.g., "*/5 * * * *" for every 5 minutes)
        cron_parts = Config.RECENT_MATCHES_CRON.split()
        if len(cron_parts) != 5:
            logger.warning(
                f"Invalid cron expression: {Config.RECENT_MATCHES_CRON}. "
                f"Using default: */5 * * * *"
            )
            cron_parts = ["*/5", "*", "*", "*", "*"]
        
        # Add recent matches job
        self.scheduler.add_job(
            recent_matches_job,
            trigger=CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4]
            ),
            id="recent_matches",
            name="Fetch Recent Matches",
            replace_existing=True
        )
        
        logger.info(f"Added job 'Fetch Recent Matches' with schedule: {Config.RECENT_MATCHES_CRON}")
    
    def start(self) -> None:
        """Start the cron worker."""
        if self.running:
            logger.warning("Cron worker is already running")
            return
        
        self.setup_jobs()
        self.scheduler.start()
        self.running = True
        logger.info("Cron worker started")
    
    def stop(self) -> None:
        """Stop the cron worker."""
        if not self.running:
            return
        
        self.scheduler.shutdown(wait=True)
        self.running = False
        logger.info("Cron worker stopped")
    
    async def run_forever(self) -> None:
        """Run the cron worker until interrupted."""
        self.start()
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Keep the event loop alive
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.stop()


async def main() -> None:
    """Main entry point."""
    Config.validate()
    DatabaseConfig().validate()  # Validate database configuration

    worker = CronWorker()
    await worker.run_forever()


if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")

