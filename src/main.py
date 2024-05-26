import uvloop
from pyrogram import idle
from pyrogram.handlers import MessageHandler
from typing import Callable

from src.loggers import logger
from src.custom_client import CustomClient
from src.message_emoji_responder import MessageEmojiResponder
from src.user_settings import UserSettings


def register_msg_handler(custom_client: CustomClient, func: Callable):
    pyrogram_response_handler: MessageHandler = MessageHandler(func)
    custom_client.add_handler(pyrogram_response_handler)


user_settings: UserSettings = UserSettings.from_config(config_file="./config.yaml")
uvloop.install()  # https://docs.pyrogram.org/topics/speedups
client: CustomClient = CustomClient(name="my_app", user_settings=user_settings)
register_msg_handler(custom_client=client, func=MessageEmojiResponder.respond)


async def main():
    async with client:
        logger.success("Telegram auth completed successfully!")
        await idle()


if __name__ == "__main__":
    client.run(main())
