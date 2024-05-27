import asyncio
from datetime import datetime, timedelta
from pyrogram.errors import FloodWait

from src.loggers import logger


class FloodWaitManager:
    @staticmethod
    async def handle(f: FloodWait) -> None:
        """
        Handles FloodWait Telegram error
        """
        resume_time = datetime.now() + timedelta(seconds=f.value)
        logger.error(
            f"FloodWait is provoked...|{f.value} s to wait\n"
            f"Program will resume at {resume_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await asyncio.sleep(f.value)
