"""
Job scheduler for automated video generation
"""

import logging
import schedule
import time
import pytz
from datetime import datetime

class VideoScheduler:
    """Schedule video generation jobs"""

    def __init__(self, config, job_function):
        self.config = config['schedule']
        self.logger = logging.getLogger(__name__)
        self.job_function = job_function
        self.timezone = pytz.timezone(self.config.get('timezone', 'UTC'))

    def setup_schedule(self):
        """Set up the schedule based on configuration"""
        if not self.config.get('enabled', True):
            self.logger.info("Scheduling is disabled")
            return

        upload_times = self.config.get('upload_times', [])

        if not upload_times:
            self.logger.warning("No upload times configured")
            return

        # Schedule jobs
        for upload_time in upload_times:
            schedule.every().day.at(upload_time).do(self.job_function)
            self.logger.info(f"Scheduled job at {upload_time} {self.config.get('timezone', 'UTC')}")

        self.logger.info(f"Scheduled {len(upload_times)} jobs per day")

    def run(self):
        """Run the scheduler (blocks)"""
        self.logger.info("Starting scheduler...")
        self.logger.info("Press Ctrl+C to stop")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")

    def run_now(self):
        """Run job immediately"""
        self.logger.info("Running job immediately...")
        self.job_function()

    def get_next_run_time(self):
        """Get the next scheduled run time"""
        jobs = schedule.jobs
        if jobs:
            next_run = min(job.next_run for job in jobs)
            return next_run
        return None

    def clear_schedule(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        self.logger.info("Schedule cleared")
