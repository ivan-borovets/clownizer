import random
from typing import Callable, Sequence
from pyrogram import Client
from pyrogram.types import User

from src.user_settings import UserSettings


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
        self.emoticon_picker: Callable[[Sequence[str]], list[str]] | None = None

    async def set_emoticon_picker(self) -> None:
        """
        Depending on the Telegram Premium status selects the way of choosing emoticons (1-3)
        """
        if self.is_premium is None:
            await self._set_premium()
        self.emoticon_picker: Callable[[Sequence[str]], list[str]] = (
            self._sample if self.is_premium else self._choice
        )

    async def _set_premium(self) -> None:
        """
        Provides the class with information about Telegram Premium status
        """
        user: User = await self.get_me()
        self.is_premium = user.is_premium

    @staticmethod
    def _choice(emoticons: Sequence[str]) -> list[str]:
        """
        Returns the list with one random emoticon from the sequence of many
        """
        return [random.choice(emoticons)]

    @staticmethod
    def _sample(emoticons: Sequence[str]) -> list[str]:
        """
        Returns the list with three random emoticons from the sequence of many
        """
        return random.sample(emoticons, k=min(3, len(emoticons)))
