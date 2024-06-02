import random
from collections import deque
from typing import Callable, Sequence

from cachetools import LRUCache
from pyrogram import Client
from pyrogram.types import User

from custom_scheduler import CustomScheduler
from user_settings import UserSettings


# pylint: disable=R0901,R0902
class CustomClient(Client):
    def __init__(
        self, name: str, user_settings: UserSettings, sleep_threshold: int = 10
    ) -> None:
        self.user_settings: UserSettings = user_settings
        super().__init__(
            name=name,
            api_id=self.user_settings.api_id,
            api_hash=self.user_settings.api_hash,
            sleep_threshold=sleep_threshold,
        )
        self.chat_info_map: dict = {}
        self.chat_emoticons_map: dict = {}
        self.chat_peer_map: dict = {}
        self.is_premium: bool | None = None
        self.emoticon_picker: Callable[[Sequence[str]], Sequence[str]] | None = None
        self.msg_queue: deque = deque(maxlen=self.user_settings.msg_queue_size)
        self.msg_keeper: LRUCache = LRUCache(maxsize=self.user_settings.msg_queue_size)
        self.scheduler: CustomScheduler = CustomScheduler(
            user_settings=self.user_settings
        )

    async def set_emoticon_picker(self) -> None:
        """
        Depending on the Telegram Premium status selects
        the way of choosing emoticons (1-3)
        """
        if self.is_premium is None:
            await self._set_premium()
        self.emoticon_picker = self._sample if self.is_premium else self._choice

    async def _set_premium(self) -> None:
        """
        Provides the class with information about Telegram Premium status
        """
        user: User = await self.get_me()
        self.is_premium = user.is_premium

    @staticmethod
    def _choice(emoticons: Sequence[str]) -> Sequence[str]:
        """
        Returns the list with one random emoticon from the sequence of many
        """
        try:
            chosen_emoticons: Sequence[str] = [random.choice(emoticons)]  # nosec
            return chosen_emoticons
        except IndexError:
            return []

    @staticmethod
    def _sample(emoticons: Sequence[str]) -> Sequence[str]:
        """
        Returns the list with three random emoticons from the sequence of many
        """
        return random.sample(emoticons, k=min(3, len(emoticons)))
