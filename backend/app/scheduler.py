import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import SCRAPE_HOUR, SCRAPE_MINUTE
from app.services.scraper_service import check_all_prices

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def daily_price_check():
    logger.info("Starting daily price check...")
    results = check_all_prices()
    logger.info(f"Daily price check complete: {results}")


def start_scheduler():
    scheduler.add_job(
        daily_price_check,
        "cron",
        hour=SCRAPE_HOUR,
        minute=SCRAPE_MINUTE,
        id="daily_price_check",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started - daily check at {SCRAPE_HOUR:02d}:{SCRAPE_MINUTE:02d}")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
