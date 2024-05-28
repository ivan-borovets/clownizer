import uvloop
from pyrogram import idle
from pyrogram.handlers import MessageHandler
from typing import Callable

from loggers import logger
from custom_client import CustomClient
from message_emoji_manager import MessageEmojiManager
from user_settings import UserSettings


def register_msg_handler(custom_client: CustomClient, func: Callable) -> None:
    """
    Registers message handler with a given function in a provided client
    """
    pyrogram_response_handler: MessageHandler = MessageHandler(func)
    custom_client.add_handler(pyrogram_response_handler)


def register_scheduler(custom_client: CustomClient, func: Callable) -> None:
    """
    Registers scheduler with a given function in a provided client
    """
    custom_client.scheduler.add_job(
        func=func,
        trigger=custom_client.scheduler.trigger,
        args=[custom_client],
        id=custom_client.name,
        replace_existing=True,
    )
    custom_client.scheduler.start()


user_settings: UserSettings = UserSettings.from_config(config_file="./config.yaml")
uvloop.install()  # https://docs.pyrogram.org/topics/speedups
client: CustomClient = CustomClient(
    name="my_app", user_settings=user_settings, sleep_threshold=0
)
message_emoji_manager: MessageEmojiManager = MessageEmojiManager()


async def main():
    async with client:
        await client.set_emoticon_picker()
        logger.success("Telegram auth completed successfully!")
        register_msg_handler(custom_client=client, func=message_emoji_manager.respond)
        register_scheduler(custom_client=client, func=message_emoji_manager.update)
        await idle()


if __name__ == "__main__":
    client.run(main())
