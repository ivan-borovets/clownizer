from pyrogram.types import Message

from src.custom_client import CustomClient


class MessageEmojiResponder:
    @classmethod
    def respond(cls, custom_client: CustomClient, message: Message):
        if not (message and message.from_user):
            return
        print(cls._chat_id_from_msg(message))

    @classmethod
    def _chat_id_from_msg(cls, message: Message):
        return message.chat.id
