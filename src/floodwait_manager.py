import asyncio
from datetime import datetime, timedelta
from pyrogram.errors import FloodWait

from src.custom_client import CustomClient
from src.loggers import logger


class FloodWaitManager:
    @staticmethod
    async def handle(f: FloodWait, custom_client: CustomClient) -> None:
        """
        Handles FloodWait Telegram error
        """
        custom_client.scheduler.pause()
        resume_time = datetime.now() + timedelta(seconds=f.value + 0.2)
        logger.error(
            f"FloodWait is provoked...|{f.value} s to wait\n"
            f"Program will resume at {resume_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await asyncio.sleep(f.value)
        custom_client.scheduler.resume()
