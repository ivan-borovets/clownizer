import random
from typing import Any, Sequence

from pyrogram.errors import FloodWait, MessageNotModified, ReactionInvalid
from pyrogram.raw import functions
from pyrogram.raw.base import Peer
from pyrogram.raw.types import ReactionEmoji
from pyrogram.types import Chat, ChatPreview, ChatReactions, Message, Reaction

import constants
from constants import FriendshipStatus
from custom_client import CustomClient
from floodwait_manager import FloodWaitManager
from loggers import logger


class MessageEmojiManager:
    # register this as message handler function for testing purposes
    # pylint: disable=W0613
    @staticmethod
    def echo(custom_client: CustomClient, message: Message):
        print(message)

    # pylint: disable=R0911
    async def respond(
        self, custom_client: CustomClient, message: Message | None
    ) -> None:
        """
        Processes incoming messages to place emojis as a response
        """
        if not self._is_valid_message(message=message):
            return None
        chat_id: int | None = self._chat_id_from_msg(message=message)
        if chat_id is None:
            return None
        if not self._is_allowed_chat(custom_client=custom_client, chat_id=chat_id):
            return None
        sender_id: int | None = self._sender_id_from_message(message=message)
        if not sender_id:
            return None
        if not self._is_target_sender(custom_client=custom_client, sender_id=sender_id):
            return None
        # for memoization and the latter functions
        await self._write_chat_info_from_id(
            custom_client=custom_client, chat_id=chat_id
        )
        emoticons_allowed: Sequence[str] = self._chat_emoticons_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        response_emoticons: Sequence[str] = self._get_response_emoticons(
            custom_client=custom_client,
            emoticons_allowed=emoticons_allowed,
            sender_id=sender_id,
        )
        if not response_emoticons:
            return None
        if not custom_client.emoticon_picker:
            return None
        picked_response_emoticons: Sequence[str] = custom_client.emoticon_picker(
            response_emoticons
        )
        response_emojis: Sequence[ReactionEmoji] = self._convert_emoticons_to_emojis(
            emoticons=picked_response_emoticons
        )
        # for memoization and the latter functions
        await self._write_chat_peer_from_id(
            custom_client=custom_client, chat_id=chat_id
        )
        chat_peer: Peer = self._peer_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        try:
            await self._place_emojis(
                custom_client=custom_client,
                peer=chat_peer,
                message_id=message.id,  # type: ignore
                emojis=response_emojis,
            )
        except (ReactionInvalid, MessageNotModified):
            pass
        else:
            self._log_method_success(
                method_name="respond",
                custom_client=custom_client,
                message=message,
                picked_response_emoticons=picked_response_emoticons,
            )
        # store message ids to retrieve it later
        # message is not None, checked in _is_valid_message()
        msg_queue_container: Sequence[int] = (chat_id, message.id)  # type: ignore
        custom_client.msg_queue.append(msg_queue_container)

    def _get_response_emoticons(
        self,
        custom_client: CustomClient,
        emoticons_allowed: Sequence[str],
        sender_id: int,
    ) -> Sequence[str]:
        """
        Calculates the intersection of allowed and preset emoticons
        Returns the resulting intersection as a sequence
        """
        sender_is_friend: bool = self._sender_is_friend(
            custom_client=custom_client, sender_id=sender_id
        )
        emoticons_from_friendship: Sequence[str] = self._emoticons_from_friendship(
            custom_client=custom_client, is_friend=sender_is_friend
        )
        response_emoticons: Sequence[str] = tuple(
            set(emoticons_allowed) & set(emoticons_from_friendship)
        )
        return response_emoticons

    @staticmethod
    def _is_valid_message(message: Message | None) -> bool:
        if message is None:
            return False
        return getattr(message, "from_user", None) is not None and bool(
            message.from_user
        )

    @staticmethod
    def _chat_id_from_msg(message: Message | None) -> int | None:
        """
        Returns chat id from a provided message
        """
        if (
            message is None
            or getattr(message, "chat", None) is None
            or not message.chat
        ):
            return None
        return message.chat.id

    def _is_allowed_chat(self, custom_client: CustomClient, chat_id: int) -> bool:
        """
        Determines whether the chat is allowed
        """
        chat_is_private: bool = self._is_chat_private(chat_id)
        chats_allowed: dict[int, str] | None = custom_client.user_settings.chats_allowed
        return chat_is_private or (
            chats_allowed is not None and chat_id in chats_allowed
        )

    @staticmethod
    def _is_chat_private(chat_id: int) -> bool:
        """
        Determines whether the chat is private
        """
        return chat_id > 0

    @staticmethod
    def _sender_id_from_message(message: Message | None) -> int | None:
        """
        Returns sender id for a given message
        """
        if (
            message is None
            or getattr(message, "from_user", None) is None
            or not message.from_user
        ):
            return None
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
        chat_info: Chat | ChatPreview | None = custom_client.chat_info_map.get(
            chat_id, None
        )
        if chat_info is not None:
            return None
        chat_info = await custom_client.get_chat(chat_id=chat_id)
        if isinstance(chat_info, Chat):
            custom_client.chat_info_map.setdefault(chat_id, chat_info)
        return None

    @staticmethod
    def _chat_attribute_from_chat_id(
        custom_client: CustomClient, chat_id: int, attribute: str
    ) -> Any:
        """
        Returns chat attribute for a given id (for a saved chat map)
        """
        chat_info: Chat | None = custom_client.chat_info_map.get(chat_id, None)
        return getattr(chat_info, attribute, None)

    def _chat_emoticons_from_chat_id(
        self, custom_client: CustomClient, chat_id: int
    ) -> Sequence[str]:
        """
        Returns a sequence of emoticons that are allowed in a chat with a given id

        The confusing logic is due to the different structure of the response
        depending on the chat settings
        """
        emoticons_allowed: Sequence[str] = custom_client.chat_emoticons_map.get(
            chat_id, ()
        )
        if emoticons_allowed:
            return emoticons_allowed
        available_reactions: ChatReactions = self._chat_attribute_from_chat_id(
            custom_client=custom_client,
            chat_id=chat_id,
            attribute="available_reactions",
        )
        chat_is_private: bool = self._is_chat_private(chat_id)
        if available_reactions is None and not chat_is_private:
            custom_client.chat_emoticons_map.setdefault(chat_id, ())
            return ()
        if chat_is_private or available_reactions.all_are_enabled:
            custom_client.chat_emoticons_map.setdefault(
                chat_id, constants.VALID_EMOTICONS
            )
            return constants.VALID_EMOTICONS
        chat_reactions: Sequence[Reaction] | None = available_reactions.reactions
        if not chat_reactions:
            custom_client.chat_emoticons_map.setdefault(chat_id, ())
            return ()
        emoticons_allowed = tuple(
            reaction.emoji for reaction in chat_reactions  # type: ignore
        )
        custom_client.chat_emoticons_map.setdefault(chat_id, emoticons_allowed)
        return emoticons_allowed

    @staticmethod
    def _sender_is_friend(custom_client: CustomClient, sender_id: int) -> bool:
        """
        For a given sender returns the friendship status
        """
        sender_info: tuple[str, FriendshipStatus] | None = (
            custom_client.user_settings.targets.get(sender_id, None)
        )
        if sender_info is None:
            return False
        _, status = sender_info
        return status == constants.FriendshipStatus.FRIEND

    @staticmethod
    def _emoticons_from_friendship(
        custom_client: CustomClient, is_friend: bool
    ) -> Sequence[str]:
        """
        For a given friendship status of a target returns corresponding emoticons
        """
        return (
            custom_client.user_settings.emoticons_for_friends
            if is_friend
            else custom_client.user_settings.emoticons_for_enemies
        )

    @staticmethod
    def _convert_emoticons_to_emojis(
        emoticons: Sequence[str],
    ) -> Sequence[ReactionEmoji]:
        """
        Converts emoticons of type string into ReactionEmojis
        """
        return [ReactionEmoji(emoticon=emoticon) for emoticon in emoticons]

    @staticmethod
    def _convert_emojis_to_emoticons(emojis: Sequence[ReactionEmoji]) -> Sequence[str]:
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
            return None
        chat_peer = await custom_client.resolve_peer(peer_id=chat_id)
        custom_client.chat_peer_map.setdefault(chat_id, chat_peer)
        return None

    @staticmethod
    def _peer_from_chat_id(custom_client: CustomClient, chat_id: int) -> Peer:
        """
        Returns chat peer for a given id
        """
        peer: Peer = custom_client.chat_peer_map.get(chat_id, None)
        return peer

    async def _place_emojis(
        self,
        custom_client: CustomClient,
        peer: Peer,
        message_id: int,
        emojis: Sequence[ReactionEmoji],
    ) -> None:
        """
        Places ReactionEmojis from a sequence of ReactionEmojis on message if possible
        """
        while True:
            try:
                await custom_client.invoke(
                    functions.messages.SendReaction(
                        peer=peer,  # type: ignore
                        msg_id=message_id,
                        add_to_recent=True,
                        reaction=list(emojis),
                    )
                )
                return None
            except ReactionInvalid:
                emoticons = ", ".join(self._convert_emojis_to_emoticons(emojis))
                logger.error(
                    f"Reactions {emoticons} were not sent!\n"
                    f"Some of these reactions are invalid in this chat.\n"
                    f"You can try to restart the app or to correct the config file."
                )
                raise
            except MessageNotModified:
                logger.error("Message was not modified. The modification is outdated.")
                raise
            except FloodWait as f:
                await FloodWaitManager.handle(f=f, custom_client=custom_client)

    @staticmethod
    def _sender_name_from_message(message: Message | None) -> str | None:
        """
        Returns sender name for a given message
        """
        if (
            message is None
            or getattr(message, "from_user", None) is None
            or not message.from_user
        ):
            return None
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
        message: Message | None,
        picked_response_emoticons: Sequence[str],
    ) -> None:
        """
        Logs a successful method execution
        """
        if message is None or getattr(message, "link", None) is None:
            logger.error("Success log failed. Message is outdated.")
            return None
        chat_id: int | None = self._chat_id_from_msg(message=message)
        if not chat_id:
            logger.error("Success log failed. Message is outdated.")
            return None
        chat_title: str = self._chat_title_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        recipient_name: str = self._sender_name_from_message(message=message) or ""
        response_emoticons: str = "".join(picked_response_emoticons)
        url: str = message.link if message.link and "-" not in message.link else "NoURL"
        log_msg: str = (
            f"{method_name}|{recipient_name}|{chat_title}|{response_emoticons}|{url}"
        )
        logger.success(log_msg)
        return None

    # pylint: disable=R0911
    async def update(self, custom_client: CustomClient) -> None:
        """
        Processes previously processed messages, updating emojis
        """
        if not custom_client.msg_queue:
            return None
        message: Message | None = await self._get_random_msg_from_queue(
            custom_client=custom_client
        )
        if message is None:
            return None
        chat_id: int | None = self._chat_id_from_msg(message=message)
        if not chat_id:
            return None
        emoticons_allowed: Sequence[str] = self._chat_emoticons_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        # we don't want to update no or single emoji
        if len(emoticons_allowed) < 2:
            return None
        sender_id: int | None = self._sender_id_from_message(message=message)
        if not sender_id:
            return None
        response_emoticons: Sequence[str] = self._get_response_emoticons(
            custom_client=custom_client,
            emoticons_allowed=emoticons_allowed,
            sender_id=sender_id,
        )
        if not response_emoticons:
            return None
        msg_emoticons: Sequence[str] | None = self._msg_emoticons_from_msg(
            message=message
        )
        if not msg_emoticons:
            return None
        # we don't want to place the same emojis
        if set(response_emoticons) <= set(msg_emoticons):
            return None
        new_response_emoticons: Sequence[str] = self._generate_different_emoticons(
            custom_client=custom_client,
            msg_emoticons=msg_emoticons,
            response_emoticons=response_emoticons,
        )
        response_emojis: Sequence[ReactionEmoji] = self._convert_emoticons_to_emojis(
            emoticons=new_response_emoticons
        )
        chat_peer: Peer = self._peer_from_chat_id(
            custom_client=custom_client, chat_id=chat_id
        )
        try:
            await self._place_emojis(
                custom_client=custom_client,
                peer=chat_peer,
                message_id=message.id,
                emojis=response_emojis,
            )
        except (ReactionInvalid, MessageNotModified):
            pass
        else:
            self._log_method_success(
                method_name="update",
                custom_client=custom_client,
                message=message,
                picked_response_emoticons=new_response_emoticons,
            )

    async def _get_random_msg_from_queue(
        self, custom_client: CustomClient
    ) -> Message | None:
        """
        Returns random message from a custom client message queue with ids tuples
        """
        msg_queue_container: tuple[int] = random.choice(  # nosec
            custom_client.msg_queue
        )
        message: Message | None = custom_client.msg_keeper.get(
            msg_queue_container, None
        )
        if message:
            return message
        message = await self._get_message_from_client(
            custom_client=custom_client, msg_queue_container=msg_queue_container
        )
        if message is None:
            return None
        custom_client.msg_keeper.setdefault(key=msg_queue_container, default=message)
        return message

    @staticmethod
    async def _get_message_from_client(
        custom_client: CustomClient, msg_queue_container: tuple[int]
    ) -> Message | None:
        """
        Returns a message through a client request with ids tuple
        """
        while True:
            try:
                message: Message | list[Message] = await custom_client.get_messages(
                    *msg_queue_container
                )
                return message if isinstance(message, Message) else None
            except FloodWait as f:
                await FloodWaitManager.handle(f, custom_client=custom_client)

    @staticmethod
    def _generate_different_emoticons(
        custom_client: CustomClient,
        msg_emoticons: Sequence[str],
        response_emoticons: Sequence[str],
    ) -> Sequence[str]:
        """
        Receives collections of previously installed emoticons and
        available emoticons and generates a different one from the original one
        """
        if not hasattr(custom_client, "emoticon_picker") or not callable(
            custom_client.emoticon_picker
        ):
            logger.error(
                "Custom client does not have a callable method `emoticon_picker`"
            )
            raise ValueError
        msg_emoticons_set: set[str] = set(msg_emoticons)
        while True:
            new_picked_response_emoticons_set: set[str] = set(
                custom_client.emoticon_picker(response_emoticons)
            )
            if msg_emoticons_set == new_picked_response_emoticons_set:
                logger.info(
                    "The generated emoticons are the same as previously placed.\n"
                    "Generating a different set of emoticons..."
                )
            else:
                return list(new_picked_response_emoticons_set)

    @staticmethod
    def _msg_emoticons_from_msg(message: Message) -> Sequence[str] | None:
        """
        Returns a sequence of placed reactions from a given message
        """
        if (
            message is None
            or getattr(message, "reactions", None) is None
            or not message.reactions
        ):
            return None
        msg_reactions: Sequence[Reaction] = message.reactions.reactions  # type: ignore
        msg_emoticons: Sequence[str] | None = tuple(
            reaction.emoji for reaction in msg_reactions  # type: ignore
        )
        return msg_emoticons
