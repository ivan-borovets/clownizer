from pyrogram import Client
from pyrogram.types import User

from src.user_settings import UserSettings


class CustomClient(Client):
    def __init__(self, name: str, user_settings: UserSettings) -> None:
        self.user_settings: UserSettings = user_settings
        super().__init__(
            name=name,
            api_id=self.user_settings.api_id,
            api_hash=self.user_settings.api_hash,
        )
        self.chat_info_map: dict = {}
        self.chat_emoticons_map: dict = {}
        self.is_premium: bool | None = None

    async def set_premium(self) -> None:
        """
        Provides the class with information about Telegram Premium status
        """
        user: User = await self.get_me()
        self.is_premium = user.is_premium
