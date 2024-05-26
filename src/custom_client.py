from pyrogram import Client

from src.user_settings import UserSettings


class CustomClient(Client):
    def __init__(self, name: str, user_settings: UserSettings) -> None:
        self.user_settings = user_settings
        super().__init__(
            name=name,
            api_id=self.user_settings.api_id,
            api_hash=self.user_settings.api_hash,
        )
