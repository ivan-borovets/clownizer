import os
import random
import uvloop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collections import deque
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.types import User

import settings

load_dotenv()
uvloop.install()  # https://docs.pyrogram.org/topics/speedups


class Context:
    is_premium = None
    last_messages = deque(maxlen=settings.MSG_QUEUE_SIZE)
    emoticon_picker: callable = None
    current_scheduler: AsyncIOScheduler = None

    app: Client = Client(
        name="my_account",
        api_id=os.getenv("API_ID"),
        api_hash=os.getenv("API_HASH"),
    )

    @classmethod
    async def set_premium(cls, client: Client) -> None:
        """
        Provides the class with information about Telegram Premium status
        """
        user: User = await client.get_me()
        cls.is_premium = user.is_premium

    @classmethod
    async def set_emoticon_picker(cls, client: Client) -> None:
        """
        Depending on the Telegram Premium status selects the way of choosing emoticons (1-3)
        """
        if cls.is_premium is None:
            await cls.set_premium(client)
        cls.emoticon_picker = (
            cls.EmoticonPickMethods.choice,
            cls.EmoticonPickMethods.sample,
        )[cls.is_premium]

    class EmoticonPickMethods:
        @staticmethod
        def choice(emoticons: tuple[str]) -> list[str]:
            """
            Returns the list with one random emoticon from the tuple of many
            """
            result = random.choice(emoticons)
            return [result]

        @staticmethod
        def sample(emoticons: tuple[str]) -> list[str]:
            """
            Returns the list with three random emoticons from the tuple of many
            """
            return random.sample(emoticons, k=min(3, len(emoticons)))
