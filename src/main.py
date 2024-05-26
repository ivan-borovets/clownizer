import uvloop
from pyrogram import idle

from src.loggers import logger
from src.custom_client import CustomClient
from src.user_settings import UserSettings

uvloop.install()  # https://docs.pyrogram.org/topics/speedups


user_settings: UserSettings = UserSettings.from_config(config_file="./config.yaml")
client: CustomClient = CustomClient(name="my_app", user_settings=user_settings)


async def main():
    async with client:
        logger.success("Telegram auth completed successfully!")
        await idle()


if __name__ == "__main__":
    client.run(main())
