import random
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
    async def respond(self, custom_client: CustomClient, message: Message) -> None:
        """
        Processes incoming messages to place emojis as a response
        """
        if not self._is_valid_message(message=message):
            return

        chat_id: int = self._chat_id_from_msg(message=message)
        if not self._is_allowed_chat(custom_client=custom_client, chat_id=chat_id):
            return

        sender_id: int = self._sender_id_from_message(message=message)
        if not self._is_target_sender(custom_client=custom_client, sender_id=sender_id):
            return

        # for memoization and the latter functions
        await self._write_chat_info_from_id(
            custom_client=custom_client, chat_id=chat_id
        )

        response_emoticons: tuple[str] = self._get_response_emoticons(
            custom_client=custom_client, chat_id=chat_id, sender_id=sender_id
        )
        picked_response_emoticons: list[str] = custom_client.emoticon_picker(
            response_emoticons
        )
        response_emojis: list[ReactionEmoji] = self._convert_emoticons_to_emojis(
            emoticons=picked_response_emoticons
        )

        # for memoization and the latter functions
        await self._write_chat_peer_from_id(
            custom_client=custom_client, chat_id=chat_id
        )

        chat_peer: Peer = self._peer_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        await self._place_emojis(
            custom_client=custom_client,
            peer=chat_peer,
            message=message,
            emojis=response_emojis,
        )
        self._log_method_success(
            method_name="respond",
            custom_client=custom_client,
            message=message,
            picked_response_emoticons=picked_response_emoticons,
        )
        # store message ids to retrieve it later
        msg_queue_container: tuple[int] = (chat_id, message.id)
        custom_client.msg_queue.append(msg_queue_container)

    def _get_response_emoticons(
        self,
        custom_client: CustomClient,
        chat_id: int,
        sender_id: int,
    ) -> tuple[str]:
        """
        Calculates the intersection of allowed and preset emoticons
        Returns the resulting intersection as a tuple
        """
        emoticons_allowed: tuple[str] | None = self._chat_emoticons_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        if emoticons_allowed is None:
            return ()
        sender_is_friend: bool = self._sender_is_friend(
            custom_client=custom_client, sender_id=sender_id
        )
        emoticons_from_friendship: tuple[str] = self._emoticons_from_friendship(
            custom_client=custom_client, is_friend=sender_is_friend
        )
        response_emoticons: tuple[str] = (
            tuple(set(emoticons_allowed) & set(emoticons_from_friendship)) or ()
        )
        return response_emoticons

    @staticmethod
    def _is_valid_message(message: Message) -> bool:
        return getattr(message, "from_user", None) is not None and message.from_user

    @staticmethod
    def _chat_id_from_msg(message: Message) -> int:
        """
        Returns chat id from a provided message
        """
        return message.chat.id

    def _is_allowed_chat(self, custom_client: CustomClient, chat_id: int) -> bool:
        """
        Determines whether the chat is allowed
        """
        chat_is_private: bool = self._is_chat_private(chat_id)
        return chat_is_private or chat_id in custom_client.user_settings.chats_allowed

    @staticmethod
    def _is_chat_private(chat_id: int) -> bool:
        """
        Determines whether the chat is private
        """
        return chat_id > 0

    @staticmethod
    def _sender_id_from_message(message: Message) -> int:
        """
        Returns sender id for a given message
        """
        return message.from_user.id

    @staticmethod
    def _is_target_sender(custom_client: CustomClient, sender_id: int) -> bool:
        """
        Determines whether the sender is a target
        """
        return sender_id in custom_client.user_settings.targets

    @staticmethod
    async def _write_chat_info_from_id(
        custom_client: CustomClient, chat_id: int
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

    @staticmethod
    def _chat_attribute_from_chat_id(
        custom_client: CustomClient, chat_id: int, attribute: str
    ) -> Any:
        """
        Returns chat attribute for a given id (for a saved chat map)
        """
        chat_info: Chat = custom_client.chat_info_map.get(chat_id)
        return getattr(chat_info, attribute, None)

    def _chat_emoticons_from_chat_id(
        self, custom_client: CustomClient, chat_id: int
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
        available_reactions: ChatReactions = self._chat_attribute_from_chat_id(
            custom_client=custom_client,
            chat_id=chat_id,
            attribute="available_reactions",
        )
        chat_is_private: bool = self._is_chat_private(chat_id)
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

    @staticmethod
    def _sender_is_friend(custom_client: CustomClient, sender_id: int) -> bool:
        """
        For a given sender returns the friendship status
        """
        sender_info = custom_client.user_settings.targets.get(sender_id)
        _, status = sender_info
        return status == constants.FriendshipStatus.FRIEND

    @staticmethod
    def _emoticons_from_friendship(
        custom_client: CustomClient, is_friend: bool
    ) -> tuple[str]:
        """
        For a given friendship status of a target returns corresponding emoticons
        """
        return (
            custom_client.user_settings.emoticons_for_friends
            if is_friend
            else custom_client.user_settings.emoticons_for_friends
        )

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

    @staticmethod
    async def _write_chat_peer_from_id(
        custom_client: CustomClient, chat_id: int
    ) -> None:
        """
        Retrieves chat peer for a given id and puts it in a client attribute
        """
        chat_peer: Peer = custom_client.chat_peer_map.get(chat_id, None)
        if chat_peer is not None:
            return
        chat_peer: Peer = await custom_client.resolve_peer(peer_id=chat_id)
        custom_client.chat_peer_map.setdefault(chat_id, chat_peer)
        return

    @staticmethod
    def _peer_from_chat_id(custom_client: CustomClient, chat_id: int) -> Peer:
        """
        Returns chat peer for a given id
        """
        peer: Peer = custom_client.chat_peer_map.get(chat_id)
        return peer

    async def _place_emojis(
        self,
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
                emoticons = ", ".join(self._convert_emojis_to_emoticons(emojis))
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

    @staticmethod
    def _sender_name_from_message(message: Message) -> str:
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

    def _chat_title_from_chat_id(self, custom_client, chat_id: int) -> str:
        """
        Returns chat title for a given id
        """
        chat_is_private: bool = self._is_chat_private(chat_id)
        if not chat_is_private:
            chat_title: str = self._chat_attribute_from_chat_id(
                custom_client=custom_client, chat_id=chat_id, attribute="title"
            )
            return chat_title
        first_name = (
            self._chat_attribute_from_chat_id(
                custom_client=custom_client, chat_id=chat_id, attribute="first_name"
            )
            or ""
        )
        last_name = (
            self._chat_attribute_from_chat_id(
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

    def _log_method_success(
        self,
        method_name: str,
        custom_client: CustomClient,
        message: Message,
        picked_response_emoticons: list[str],
    ) -> None:
        """
        Logs a successful method execution
        """
        chat_id: int = self._chat_id_from_msg(message=message)
        chat_title: str = self._chat_title_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        recipient_name: str = self._sender_name_from_message(message=message)
        response_emoticons: str = "".join(picked_response_emoticons)
        url = message.link if message.link and "-" not in message.link else "NoURL"
        log_msg = (
            f"{method_name}|{recipient_name}|{chat_title}|{response_emoticons}|{url}"
        )
        logger.success(log_msg)

    async def update(self, custom_client: CustomClient) -> None:
        """
        Processes previously processed messages, updating emojis
        """
        if not custom_client.msg_queue:
            return
        message: Message | None = await self._get_random_msg_from_queue(
            custom_client=custom_client
        )
        if not message:
            return
        print(message.chat.id, message.id)
        print(custom_client.msg_keeper)

    async def _get_random_msg_from_queue(
        self, custom_client: CustomClient
    ) -> Message | None:
        """
        Returns random message from a custom client message queue with ids tuples
        """
        msg_queue_container: tuple[int] = random.choice(custom_client.msg_queue)
        message: Message | None = custom_client.msg_keeper.get(
            msg_queue_container, None
        )
        if message:
            return message
        message = await self._get_message_from_client(
            custom_client=custom_client, msg_queue_container=msg_queue_container
        )
        if message:
            custom_client.msg_keeper.setdefault(
                key=msg_queue_container, default=message
            )
            return message
        return

    @staticmethod
    async def _get_message_from_client(
        custom_client: CustomClient, msg_queue_container: tuple[int]
    ) -> Message | None:
        """
        Returns a message through a client request with ids tuple
        """
        while True:
            try:
                message: Message = await custom_client.get_messages(
                    *msg_queue_container
                )
                return message
            except FloodWait as f:
                await FloodWaitManager.handle(f)
