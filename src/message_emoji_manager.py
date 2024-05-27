from pyrogram.errors import ReactionInvalid, MessageNotModified, FloodWait
from pyrogram.raw import functions
from pyrogram.raw.base import Peer
from pyrogram.raw.types import ReactionEmoji
from pyrogram.types import Message, Chat, Reaction, ChatReactions
from typing import Any, Sequence

from src import constants
from src.custom_client import CustomClient
from src.floodwait_manager import FloodWaitManager
from src.loggers import logger


class MessageEmojiManager:
    @classmethod
    async def respond(cls, custom_client: CustomClient, message: Message) -> None:
        """
        Processes incoming messages to place emojis as a response
        """
        if getattr(message, "from_user", None) is None or not message.from_user:
            return
        chat_id: int = cls._chat_id_from_msg(message=message)
        chat_is_private: bool = cls._is_chat_private(chat_id)
        if (
            not chat_is_private
            and chat_id not in custom_client.user_settings.chats_allowed
        ):
            return
        sender_id: int = cls._sender_id_from_message(message=message)
        if sender_id not in custom_client.user_settings.targets:
            return
        await cls._write_chat_info_from_id(custom_client=custom_client, chat_id=chat_id)
        emoticons_allowed: tuple[str] | None = cls._chat_emoticons_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        if emoticons_allowed is None:
            return
        sender_is_friend: bool = cls._sender_is_friend(
            custom_client=custom_client, sender_id=sender_id
        )
        emoticons_from_friendship: tuple[str] = cls._emoticons_from_friendship(
            custom_client=custom_client, is_friend=sender_is_friend
        )
        response_emoticons: tuple[str] = tuple(
            set(emoticons_allowed) & set(emoticons_from_friendship)
        )
        if not response_emoticons:
            return
        picked_response_emoticons: list[str] = custom_client.emoticon_picker(
            response_emoticons
        )
        response_emojis: list[ReactionEmoji] = cls._convert_emoticons_to_emojis(
            emoticons=picked_response_emoticons
        )
        await cls._write_chat_peer_from_id(custom_client=custom_client, chat_id=chat_id)
        chat_peer: Peer = cls._peer_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        await cls._place_emojis(
            custom_client=custom_client,
            peer=chat_peer,
            message=message,
            emojis=response_emojis,
        )

    @classmethod
    def _chat_id_from_msg(cls, message: Message) -> int:
        """
        Returns chat id from a provided message
        """
        return message.chat.id

    @classmethod
    def _is_chat_private(cls, chat_id: int) -> bool:
        """
        Determines whether the chat is private
        """
        return chat_id > 0

    @classmethod
    def _sender_id_from_message(cls, message: Message) -> int:
        """
        Returns sender id for a given message
        """
        return message.from_user.id

    @classmethod
    def _sender_name_from_message(cls, message: Message) -> str:
        """
        Returns sender name for a given message
        """
        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        full_name = (
            f"{first_name} {last_name}".strip()
            if first_name or last_name
            else "No Name"
        )
        return full_name

    @classmethod
    def _sender_is_friend(cls, custom_client: CustomClient, sender_id: int) -> bool:
        """
        For a given sender returns the friendship status
        """
        sender_info = custom_client.user_settings.targets.get(sender_id)
        _, status = sender_info
        return status == constants.FriendshipStatus.FRIEND

    @classmethod
    def _emoticons_from_friendship(
        cls, custom_client: CustomClient, is_friend: bool
    ) -> tuple[str]:
        """
        For a given friendship status of a target returns corresponding emoticons
        """
        return (
            custom_client.user_settings.emoticons_for_friends
            if is_friend
            else custom_client.user_settings.emoticons_for_friends
        )

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
    async def _write_chat_peer_from_id(
        cls, custom_client: CustomClient, chat_id: int
    ) -> None:
        """
        Retrieves chat peer for a given id and puts it in a client attribute
        """
        chat_peer: Peer = custom_client.chat_peer_map.get(chat_id, None)
        if chat_peer is not None:
            return
        chat_peer: Peer = await custom_client.resolve_peer(peer_id=chat_id)
        custom_client.chat_peer_map.setdefault(chat_id, chat_peer)
        print(chat_peer)
        return

    @classmethod
    def _chat_attribute_from_chat_id(
        cls, custom_client: CustomClient, chat_id: int, attribute: str
    ) -> Any:
        """
        Returns chat attribute for a given id (for a saved chat map)
        """
        chat_info: Chat = custom_client.chat_info_map.get(chat_id)
        return getattr(chat_info, attribute, None)

    @classmethod
    def _chat_emoticons_from_chat_id(
        cls, custom_client: CustomClient, chat_id: int
    ) -> tuple[str] | None:
        """
        Returns a list of emoticons that are allowed in a chat with a given id

        The confusing logic is due to the different structure of the response depending on the chat settings
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
        chat_is_private: bool = cls._is_chat_private(chat_id)
        if available_reactions is None and not chat_is_private:
            custom_client.chat_emoticons_map.setdefault(chat_id, ())
            return
        if chat_is_private or available_reactions.all_are_enabled:
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
        chat_is_private: bool = cls._is_chat_private(chat_id)
        if not chat_is_private:
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
            f"{first_name} {last_name}".strip()
            if first_name or last_name
            else "No Name"
        )
        return chat_title

    @classmethod
    def _peer_from_chat_id(cls, custom_client: CustomClient, chat_id: int) -> Peer:
        """
        Returns chat peer for a given id
        """
        peer: Peer = custom_client.chat_peer_map.get(chat_id)
        return peer

    @staticmethod
    def _convert_emoticons_to_emojis(emoticons: Sequence[str]) -> list[ReactionEmoji]:
        """
        Converts emoticons of type string into ReactionEmojis
        """
        return [ReactionEmoji(emoticon=emoticon) for emoticon in emoticons]

    @staticmethod
    def _convert_emojis_to_emoticons(emojis: Sequence[ReactionEmoji]) -> list[str]:
        """
        Converts ReactionEmojis into emoticons of type string
        """
        return [emoji.emoticon for emoji in emojis]

    @classmethod
    async def _place_emojis(
        cls,
        custom_client: CustomClient,
        peer: Peer,
        message: Message,
        emojis: list[ReactionEmoji],
    ) -> None:
        """
        Places ReactionEmojis from a list of ReactionEmojis on message if possible
        """
        while True:
            try:
                await custom_client.invoke(
                    functions.messages.SendReaction(
                        peer=peer,
                        msg_id=message.id,
                        add_to_recent=True,
                        reaction=emojis,
                    )
                )
                break
            except ReactionInvalid:
                emoticons = ", ".join(cls._convert_emojis_to_emoticons(emojis))
                logger.error(
                    f"Reactions {emoticons} were not sent!\n"
                    f"Some of these reactions are invalid in this chat.\n"
                    f"You can try to correct the config file."
                )
                break
            except MessageNotModified:
                logger.error("Message was not modified. The modification is outdated.")
                break
            except FloodWait as f:
                await FloodWaitManager.handle(f)
