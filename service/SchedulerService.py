import logging
from apscheduler.schedulers.background import BackgroundScheduler
from service.GlucoseMonitorService import fetch_glucose_readings_for_all_users

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(fetch_glucose_readings_for_all_users, 'interval', seconds=60)

    def start(self):
        logger.info("Starting background scheduler for glucose readings...")
        self.scheduler.start()
        logger.info("✓ Scheduler started - glucose readings will be fetched every 60 seconds")

    def shutdown(self):
        logger.info("Shutting down background scheduler...")
        self.scheduler.shutdown()
        logger.info("✓ Scheduler stopped")