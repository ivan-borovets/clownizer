from pyrogram.types import Message, Chat, Reaction

from src.custom_client import CustomClient


class MessageEmojiResponder:
    @classmethod
    async def respond(cls, custom_client: CustomClient, message: Message) -> None:
        """
        Processes incoming messages to place emojis as a response
        """
        if not (message and message.from_user):
            return
        chat_id = cls._chat_id_from_msg(message=message)
        chat_emoticons = await cls._chat_emoticons_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        print(chat_emoticons)

    @classmethod
    def _chat_id_from_msg(cls, message: Message) -> int:
        """
        Returns chat id from a provided message
        """
        return message.chat.id

    @classmethod
    async def _chat_emoticons_from_chat_id(
        cls, custom_client: CustomClient, chat_id: int
    ) -> list[str] | None:
        """
        Returns a list of emoticons that are allowed in a chat with a given id
        """
        chat_properties: Chat = await custom_client.get_chat(chat_id=chat_id)
        if getattr(chat_properties, "available_reactions", None) is None:
            return
        chat_reactions: list[Reaction] = chat_properties.available_reactions.reactions
        emoticons_allowed: list[str] = [reaction.emoji for reaction in chat_reactions]
        return emoticons_allowed
