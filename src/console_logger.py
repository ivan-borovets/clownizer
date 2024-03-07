from pyrogram.raw.types import ReactionEmoji
from pyrogram.types import Message
from settings import logger


class ConsoleLogger:
    @staticmethod
    async def log(fun_name: str, message: Message, emojis: list[ReactionEmoji]) -> None:
        """
        Makes SUCCESS logs more descriptive.
        """
        emoticons = ", ".join(e.emoticon for e in emojis)
        recipient = f"{message.from_user.first_name} {message.from_user.last_name}"
        url = message.link if message.link and "-" not in message.link else "NoURL"
        chat_name = message.chat.title if message.chat.title else "NoChatName"
        logger.success(f"{fun_name}|{recipient}|{chat_name}|{emoticons}\n{url}")
