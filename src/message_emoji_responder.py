from typing import Any
from pyrogram.types import Message, Chat, Reaction, ChatReactions
from pyrogram.enums import ChatType

from src import constants
from src.custom_client import CustomClient


class MessageEmojiManager:
    @classmethod
    async def respond(cls, custom_client: CustomClient, message: Message) -> None:
        """
        Processes incoming messages to place emojis as a response
        """
        if getattr(message, "from_user", None) is None or not message.from_user:
            return
        chat_id: int = cls._chat_id_from_msg(message=message)
        await cls._write_chat_info_from_id(custom_client=custom_client, chat_id=chat_id)
        print(
            "emoticons",
            cls._chat_emoticons_from_chat_id(
                custom_client=custom_client, chat_id=chat_id
            ),
        )
        print(
            "chat_title",
            cls._chat_title_from_chat_id(custom_client=custom_client, chat_id=chat_id),
        )

    @classmethod
    def _chat_id_from_msg(cls, message: Message) -> int:
        """
        Returns chat id from a provided message
        """
        return message.chat.id

    @classmethod
    async def _write_chat_info_from_id(
        cls, custom_client: CustomClient, chat_id: int
    ) -> None:
        """
        Retrieves chat info for a given id and puts it in a client attribute
        """
        chat_info: Chat | None = custom_client.chat_info_map.get(chat_id, None)
        if chat_info is not None:
            return
        chat_info: Chat = await custom_client.get_chat(chat_id=chat_id)
        custom_client.chat_info_map.setdefault(chat_id, chat_info)
        return

    @classmethod
    def _chat_attribute_from_chat_id(
        cls, custom_client: CustomClient, chat_id: int, attribute: str
    ) -> Any:
        """
        Returns chat attribute for a given id
        """
        chat_info: Chat = custom_client.chat_info_map.get(chat_id)
        return getattr(chat_info, attribute, None)

    @classmethod
    def _chat_emoticons_from_chat_id(
        cls, custom_client: CustomClient, chat_id: int
    ) -> tuple[str] | None:
        """
        Returns a list of emoticons that are allowed in a chat with a given id.

        The confusing logic is due to the different structure of the response depending on the chat settings.
        """
        emoticons_allowed: tuple[str] | None = custom_client.chat_emoticons_map.get(
            chat_id, None
        )
        if emoticons_allowed is not None:
            return emoticons_allowed
        available_reactions: ChatReactions = cls._chat_attribute_from_chat_id(
            custom_client=custom_client,
            chat_id=chat_id,
            attribute="available_reactions",
        )
        chat_type: ChatType = cls._chat_attribute_from_chat_id(
            custom_client=custom_client, chat_id=chat_id, attribute="type"
        )
        if available_reactions is None and chat_type != ChatType.PRIVATE:
            custom_client.chat_emoticons_map.setdefault(chat_id, ())
            return
        if chat_type == ChatType.PRIVATE or available_reactions.all_are_enabled:
            custom_client.chat_emoticons_map.setdefault(
                chat_id, constants.VALID_EMOTICONS
            )
            return constants.VALID_EMOTICONS
        chat_reactions: list[Reaction] = available_reactions.reactions
        emoticons_allowed: tuple[str] = tuple(
            reaction.emoji for reaction in chat_reactions
        )
        custom_client.chat_emoticons_map.setdefault(chat_id, emoticons_allowed)
        return emoticons_allowed

    @classmethod
    def _chat_title_from_chat_id(cls, custom_client, chat_id: int) -> str:
        """
        Returns chat title for a given id
        """
        chat_type: ChatType = cls._chat_attribute_from_chat_id(
            custom_client=custom_client, chat_id=chat_id, attribute="type"
        )
        if chat_type != ChatType.PRIVATE:
            chat_title: str = cls._chat_attribute_from_chat_id(
                custom_client=custom_client, chat_id=chat_id, attribute="title"
            )
            return chat_title
        first_name = (
            cls._chat_attribute_from_chat_id(
                custom_client=custom_client, chat_id=chat_id, attribute="first_name"
            )
            or ""
        )
        last_name = (
            cls._chat_attribute_from_chat_id(
                custom_client=custom_client, chat_id=chat_id, attribute="last_name"
            )
            or ""
        )
        chat_title = (
            f"{first_name} {last_name}" if first_name and last_name else "No Name"
        )
        return chat_title
