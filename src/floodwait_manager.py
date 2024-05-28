import asyncio
from datetime import datetime, timedelta
from pyrogram.errors import FloodWait

from custom_client import CustomClient
from loggers import logger


class FloodWaitManager:
    @staticmethod
    async def handle(f: FloodWait, custom_client: CustomClient) -> None:
        """
        Handles FloodWait Telegram error
        """
        custom_client.scheduler.pause()
        resume_time = datetime.now() + timedelta(seconds=f.value)
        logger.error(
            f"FloodWait is provoked...|{f.value} s to wait\n"
            f"Program will resume at {resume_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await asyncio.sleep(f.value)
        custom_client.scheduler.resume()
