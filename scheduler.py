"""
Cron Job / Scheduler - Runs the pipeline on a schedule
Runs every N minutes (configurable)
"""
import os
import sys
import schedule
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from orchestrate import Pipeline
from utils.logger import get_logger
from utils.config import CRON_INTERVAL

logger = get_logger('scheduler')

def run_pipeline():
    """Run the pipeline"""
    logger.info(f"[{datetime.now()}] Running scheduled pipeline check...")
    pipeline = Pipeline()
    pipeline.run()

def main():
    """Start the scheduler"""
    logger.info(f"Starting scheduler - polling every {CRON_INTERVAL} minutes")

    # Run immediately on startup, then on schedule
    run_pipeline()
    schedule.every(CRON_INTERVAL).minutes.do(run_pipeline)

    # Keep scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
