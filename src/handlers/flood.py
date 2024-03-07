import asyncio
from datetime import datetime, timedelta
from pyrogram.errors import FloodWait

from handlers.scheduler_job import SchedulerJobHandler
from settings import logger


class FloodHandler:
    @staticmethod
    async def handle(e: FloodWait):
        """
        Handles FloodWait error with respect to the jobs of the scheduler
        """
        SchedulerJobHandler.stop()
        resume_time = datetime.now() + timedelta(seconds=e.value)
        logger.error(
            f"FloodWait is provoked :( |{e.value} s to wait\n"
            f"Program will resume at {resume_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await asyncio.sleep(e.value)
        SchedulerJobHandler.resume()
