from collections import deque
from typing import Any, Callable, Optional, Sequence
from unittest.mock import AsyncMock, Mock, patch

import pytest
from cachetools import LRUCache
from pyrogram.enums import ChatType
from pyrogram.errors import (
    BadRequest,
    FloodWait,
    MessageIdInvalid,
    MessageNotModified,
    NotAcceptable,
    ReactionInvalid,
)
from pyrogram.raw import functions
from pyrogram.raw.base import Peer
from pyrogram.raw.types import ReactionEmoji
from pyrogram.types import Chat, Message, Reaction, User
from pyrogram.types.messages_and_media.message import Str

import src.constants
from src.custom_client import CustomClient
from src.floodwait_manager import FloodWaitManager
from src.message_emoji_manager import MessageEmojiManager as Manager


class TestEcho:
    @staticmethod
    def test_echo(mock_message: Message) -> None:
        with patch("builtins.print") as mock_print:
            Manager.echo(message=mock_message)
            mock_print.assert_called_once_with(mock_message)

        return None


class TestRespond:
    @staticmethod
    @pytest.mark.asyncio
    async def test_valid_message(
        test_custom_client: CustomClient, mock_message: Message, mock_peer: Peer
    ) -> None:
        manager: Manager = Manager()
        manager._write_chat_info_from_id = AsyncMock()  # type: ignore
        manager._write_chat_peer_from_id = AsyncMock()  # type: ignore

        with patch.object(
            manager, "_chat_emoticons_from_chat_id", return_value=["👍", "👎"]
        ), patch.object(
            manager, "_peer_from_chat_id", return_value=mock_peer
        ), patch.object(
            manager, "_place_emojis", new_callable=AsyncMock
        ) as mock_place_emojis, patch.object(
            test_custom_client,
            "resolve_peer",
            new_callable=AsyncMock,
            return_value=mock_peer,
        ):
            test_custom_client.emoticon_picker = lambda x: ["👍"]
            test_custom_client.user_settings.targets = {
                mock_message.from_user.id: (
                    "Alice",
                    src.constants.FriendshipStatus.FRIEND,
                )
            }

            await manager.respond(
                custom_client=test_custom_client, message=mock_message
            )
            mock_place_emojis.assert_called_once()
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_invalid_message(test_custom_client: CustomClient) -> None:
        manager: Manager = Manager()
        message: Message | None = None
        await manager.respond(custom_client=test_custom_client, message=message)
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_invalid_chat(
        test_custom_client: CustomClient, mock_message: Message
    ) -> None:
        manager: Manager = Manager()
        mock_message.chat = None  # type: ignore
        await manager.respond(custom_client=test_custom_client, message=mock_message)
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_not_allowed_chat(
        test_custom_client: CustomClient, mock_message: Message
    ) -> None:
        manager: Manager = Manager()
        test_custom_client.user_settings.chats_allowed = {-12345: "Test Chat"}
        mock_message.chat.id = -54321
        await manager.respond(custom_client=test_custom_client, message=mock_message)
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_invalid_sender(
        test_custom_client: CustomClient, mock_message: Message
    ) -> None:
        manager: Manager = Manager()
        mock_message.from_user = None  # type: ignore
        await manager.respond(custom_client=test_custom_client, message=mock_message)
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_not_target_sender(
        test_custom_client: CustomClient, mock_message: Message
    ) -> None:
        manager: Manager = Manager()
        test_custom_client.user_settings.targets = {
            123456789: ("Alice", src.constants.FriendshipStatus.ENEMY)
        }
        mock_message.from_user.id = 987654321
        await manager.respond(custom_client=test_custom_client, message=mock_message)
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_no_emoticons(
        test_custom_client: CustomClient, mock_message: Message
    ) -> None:
        manager: Manager = Manager()
        manager._write_chat_info_from_id = AsyncMock()  # type: ignore
        with patch.object(manager, "_chat_emoticons_from_chat_id", return_value=[]):
            await manager.respond(
                custom_client=test_custom_client, message=mock_message
            )
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_no_picker(
        test_custom_client: CustomClient, mock_message: Message
    ) -> None:
        manager = Manager()
        manager._write_chat_info_from_id = AsyncMock()  # type: ignore
        with patch.object(
            manager, "_chat_emoticons_from_chat_id", return_value=["👍", "👎"]
        ):
            test_custom_client.emoticon_picker = None
            await manager.respond(
                custom_client=test_custom_client, message=mock_message
            )
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_no_chat_peer(
        test_custom_client: CustomClient, mock_message: Message
    ) -> None:
        manager: Manager = Manager()
        manager._write_chat_info_from_id = AsyncMock()  # type: ignore
        manager._write_chat_peer_from_id = AsyncMock()  # type: ignore

        with patch.object(
            manager, "_chat_emoticons_from_chat_id", return_value=["👍", "👎"]
        ), patch.object(manager, "_peer_from_chat_id", return_value=None), patch.object(
            manager, "_place_emojis", new_callable=AsyncMock
        ) as mock_place_emojis:
            test_custom_client.emoticon_picker = lambda x: ["👍"]
            test_custom_client.user_settings.targets = {
                mock_message.from_user.id: (
                    "Alice",
                    src.constants.FriendshipStatus.FRIEND,
                )
            }

            result = await manager.respond(  # type: ignore
                custom_client=test_custom_client, message=mock_message
            )
            assert result is None
            mock_place_emojis.assert_not_called()
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_success(
        test_custom_client: CustomClient, mock_message: Message, mock_peer: Peer
    ) -> None:
        manager: Manager = Manager()
        manager._write_chat_info_from_id = AsyncMock()  # type: ignore

        with patch.object(
            manager, "_chat_emoticons_from_chat_id", return_value=["👍", "👎"]
        ), patch.object(
            manager, "_peer_from_chat_id", return_value=mock_peer
        ), patch.object(
            manager, "_place_emojis", new_callable=AsyncMock
        ) as mock_place_emojis, patch.object(
            test_custom_client,
            "resolve_peer",
            new_callable=AsyncMock,
            return_value=mock_peer,
        ):
            test_custom_client.emoticon_picker = lambda x: ["👍"]
            test_custom_client.user_settings.targets = {
                mock_message.from_user.id: (
                    "Alice",
                    src.constants.FriendshipStatus.FRIEND,
                )
            }

            assert manager._is_valid_message(mock_message), "Message should be valid"
            assert (
                manager._chat_id_from_msg(mock_message) == mock_message.chat.id
            ), f"Chat ID should be {mock_message.chat.id}"
            assert manager._is_allowed_chat(
                test_custom_client, mock_message.chat.id
            ), "Chat should be allowed"
            assert (
                manager._sender_id_from_message(mock_message)
                == mock_message.from_user.id
            ), f"Sender ID should be {mock_message.from_user.id}"
            assert manager._is_target_sender(
                test_custom_client, mock_message.from_user.id
            ), "Sender should be target"

            await manager.respond(
                custom_client=test_custom_client, message=mock_message
            )
            mock_place_emojis.assert_called_once()
            return None

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "chat_id, is_allowed_chat, sender_id, is_target_sender, "
        "emoticons_allowed, emoticon_picker, peer_from_chat_id",
        [
            (
                None,
                True,
                2,
                True,
                ["👍", "👎"],
                lambda x: ["👍"],
                AsyncMock(),
            ),  # Invalid chat
            (
                1,
                False,
                2,
                True,
                ["👍", "👎"],
                lambda x: ["👍"],
                AsyncMock(),
            ),  # Not allowed chat
            (
                1,
                True,
                None,
                True,
                ["👍", "👎"],
                lambda x: ["👍"],
                AsyncMock(),
            ),  # Invalid sender
            (
                1,
                True,
                2,
                False,
                ["👍", "👎"],
                lambda x: ["👍"],
                AsyncMock(),
            ),  # Not target sender
            (1, True, 2, True, [], lambda x: ["👍"], AsyncMock()),  # No emoticons
            (1, True, 2, True, ["👍", "👎"], None, AsyncMock()),  # No picker
            (1, True, 2, True, ["👍", "👎"], lambda x: ["👍"], None),  # No chat peer
        ],
    )
    async def test_failures(
        test_custom_client: CustomClient,
        mock_message: Message,
        chat_id: int | None,
        is_allowed_chat: bool,
        sender_id: int | None,
        is_target_sender: bool,
        emoticons_allowed: Sequence[str],
        emoticon_picker: Callable,
        peer_from_chat_id: AsyncMock,
    ) -> None:
        manager: Manager = Manager()
        manager._write_chat_info_from_id = AsyncMock()  # type: ignore

        with patch.object(
            manager, "_chat_id_from_msg", return_value=chat_id
        ), patch.object(
            manager, "_is_allowed_chat", return_value=is_allowed_chat
        ), patch.object(
            manager, "_sender_id_from_message", return_value=sender_id
        ), patch.object(
            manager, "_is_target_sender", return_value=is_target_sender
        ), patch.object(
            manager, "_chat_emoticons_from_chat_id", return_value=emoticons_allowed
        ), patch.object(
            manager, "_peer_from_chat_id", return_value=peer_from_chat_id
        ), patch.object(
            manager, "_place_emojis", new_callable=AsyncMock
        ):
            test_custom_client.emoticon_picker = emoticon_picker

            test_custom_client.user_settings.targets = {
                mock_message.from_user.id: (
                    "Alice",
                    src.constants.FriendshipStatus.FRIEND,
                )
            }

            if peer_from_chat_id is None:
                with patch.object(
                    test_custom_client, "resolve_peer", new_callable=AsyncMock
                ) as mock_resolve_peer:
                    mock_resolve_peer.side_effect = ConnectionError(
                        "Client has not been started yet"
                    )
                    with pytest.raises(
                        ConnectionError, match="Client has not been started yet"
                    ):
                        await manager.respond(
                            custom_client=test_custom_client, message=mock_message
                        )
                    mock_resolve_peer.assert_called_once_with(peer_id=chat_id)
            else:
                await manager.respond(
                    custom_client=test_custom_client, message=mock_message
                )
        return

    @staticmethod
    @pytest.mark.asyncio
    async def test_exception_handling(
        test_custom_client: CustomClient, mock_message: Message, mock_peer: Peer
    ) -> None:
        manager: Manager = Manager()
        manager._write_chat_info_from_id = AsyncMock()  # type: ignore
        manager._write_chat_peer_from_id = AsyncMock()  # type: ignore
        with patch.object(
            manager, "_chat_emoticons_from_chat_id", return_value=["👍"]
        ), patch.object(
            manager, "_peer_from_chat_id", return_value=mock_peer
        ), patch.object(
            manager, "_place_emojis", new_callable=AsyncMock
        ) as mock_place_emojis, patch.object(
            test_custom_client,
            "resolve_peer",
            new_callable=AsyncMock,
            return_value=mock_peer,
        ):
            test_custom_client.emoticon_picker = lambda x: ["👍"]
            test_custom_client.user_settings.targets = {
                mock_message.from_user.id: (
                    "Alice",
                    src.constants.FriendshipStatus.FRIEND,
                )
            }

            for exc in [
                ReactionInvalid,
                MessageNotModified,
                MessageIdInvalid,
                BadRequest,
                NotAcceptable,
            ]:
                mock_place_emojis.side_effect = exc()
                await manager.respond(
                    custom_client=test_custom_client, message=mock_message
                )
                assert mock_place_emojis.call_count > 0

        return None


class TestGetResponseEmoticons:
    @staticmethod
    @pytest.mark.parametrize(
        "emoticons_allowed, test_sender_id, sender_is_friend, "
        "emoticons_from_friendship, expected_result",
        [
            (("👍", "👎", "❤"), 1, True, ("👍", "❤", "🔥"), ("👍", "❤")),
            (("👍", "👎"), 2, False, ("👎", "🤡"), ("👎",)),
            (("👍", "👎"), 3, True, ("🔥",), ()),
            ((), 4, True, ("👍", "❤"), ()),
            (("👍", "👎"), 5, False, (), ()),
        ],
    )
    def test(
        emoticons_allowed: Sequence[str],
        test_sender_id: int,
        sender_is_friend: bool,
        emoticons_from_friendship: Sequence[str],
        expected_result: Sequence[str],
        test_custom_client: CustomClient,
    ) -> None:
        manager = Manager()
        manager._sender_is_friend = (  # type: ignore
            lambda custom_client, sender_id: sender_is_friend
        )
        manager._emoticons_from_friendship = (  # type: ignore
            lambda custom_client, is_friend: emoticons_from_friendship
        )

        result = manager._get_response_emoticons(
            custom_client=test_custom_client,
            emoticons_allowed=emoticons_allowed,
            sender_id=test_sender_id,
        )
        assert set(result) == set(expected_result)
        return None


class TestIsValidMessage:
    @staticmethod
    def test_none() -> None:
        assert not Manager()._is_valid_message(message=None)
        return None

    @staticmethod
    def test_not_from_user(mock_message: Message) -> None:
        mock_message.from_user = None  # type: ignore
        assert not Manager._is_valid_message(message=mock_message)
        return None

    @staticmethod
    def test_valid(mock_message: Message) -> None:
        assert Manager._is_valid_message(message=mock_message)
        return None


class TestChatIdFromMsg:
    @staticmethod
    def test_none() -> None:
        assert Manager._chat_id_from_msg(None) is None
        return None

    @staticmethod
    def test_no_chat(mock_message: Message) -> None:
        mock_message.chat = None  # type: ignore
        assert Manager._chat_id_from_msg(message=mock_message) is None
        return None

    @staticmethod
    def test_valid(mock_message: Message) -> None:
        assert Manager._chat_id_from_msg(message=mock_message) == 1
        return None


class TestIsChatPrivate:
    @staticmethod
    @pytest.mark.parametrize(
        "chat_id, expected_result", [(1, True), (0, False), (-1, False)]
    )
    def test(chat_id: int, expected_result: bool) -> None:
        assert Manager._is_chat_private(chat_id=chat_id) == expected_result
        return None


class TestIsAllowedChat:
    @staticmethod
    @pytest.mark.parametrize(
        "chat_id, chats_allowed, expected_result",
        [
            (1, None, True),  # private chat
            (0, None, False),  # public chat, no allowed
            (-12345, {-12345: "Test Chat"}, True),  # public chat allowed
            (-12345, {}, False),  # public chat, no permission
            (-12345, {12345: "Test Chat"}, False),  # public chat, no permission
        ],
    )
    def test(
        test_custom_client: CustomClient,
        chat_id: int,
        chats_allowed: dict | None,
        expected_result: bool,
    ) -> None:
        test_custom_client.user_settings.chats_allowed = chats_allowed
        manager: Manager = Manager()
        assert (
            manager._is_allowed_chat(custom_client=test_custom_client, chat_id=chat_id)
            == expected_result
        )
        return None


class TestSenderIdFromMessage:
    @staticmethod
    def test_none() -> None:
        assert Manager._sender_id_from_message(message=None) is None
        return None

    @staticmethod
    def test_no_user(mock_message: Message) -> None:
        mock_message.from_user = None  # type: ignore
        assert Manager._sender_id_from_message(message=mock_message) is None
        return None

    @staticmethod
    def test_valid(mock_message: Message) -> None:
        assert Manager._sender_id_from_message(message=mock_message) == 2
        return None


class TestIsTargetSender:
    @staticmethod
    @pytest.mark.parametrize(
        "sender_id, targets, expected_result",
        [
            (
                123456789,
                {123456789: ("Alice", src.constants.FriendshipStatus.FRIEND)},
                True,
            ),
            (
                987654321,
                {123456789: ("Alice", src.constants.FriendshipStatus.FRIEND)},
                False,
            ),
            (123456789, {}, False),
        ],
    )
    def test(
        test_custom_client: CustomClient,
        sender_id: int,
        targets: dict,
        expected_result: bool,
    ) -> None:
        test_custom_client.user_settings.targets = targets
        assert (
            Manager._is_target_sender(
                custom_client=test_custom_client, sender_id=sender_id
            )
            == expected_result
        )
        return None


class TestWriteChatInfoFromId:
    @staticmethod
    @pytest.mark.asyncio
    async def test(test_custom_client: CustomClient, mock_chat: Chat) -> None:
        test_custom_client.get_chat = AsyncMock()  # type: ignore
        test_custom_client.get_chat.return_value = mock_chat
        manager: Manager = Manager()
        chat_id: int = mock_chat.id
        await manager._write_chat_info_from_id(
            custom_client=test_custom_client, chat_id=chat_id
        )
        test_custom_client.get_chat.assert_called_once_with(chat_id=chat_id)
        assert (
            test_custom_client.chat_info_map.get(chat_id) == mock_chat  # type: ignore
        )
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_with_existing_info(
        test_custom_client: CustomClient, mock_chat: Chat
    ) -> None:
        test_custom_client.get_chat = AsyncMock()  # type: ignore
        test_custom_client.get_chat.return_value = mock_chat
        chat_id: int = mock_chat.id
        test_custom_client.chat_info_map[chat_id] = mock_chat
        manager: Manager = Manager()
        await manager._write_chat_info_from_id(
            custom_client=test_custom_client, chat_id=chat_id
        )
        test_custom_client.get_chat.assert_not_awaited()

    @staticmethod
    @pytest.mark.asyncio
    async def test_value_error(
        test_custom_client: CustomClient,
    ) -> None:
        test_custom_client.get_chat = AsyncMock(side_effect=ValueError)  # type: ignore
        manager: Manager = Manager()
        chat_id: int = 1
        await manager._write_chat_info_from_id(
            custom_client=test_custom_client, chat_id=chat_id
        )
        test_custom_client.get_chat.assert_called_once_with(chat_id=chat_id)
        return None


class TestChatAttributeFromChatId:
    @staticmethod
    def test(test_custom_client: CustomClient, mock_chat: Chat) -> None:
        mock_chat.title = "Test Chat Title"
        chat_id: int = mock_chat.id
        test_custom_client.chat_info_map[chat_id] = mock_chat
        attribute = "title"
        expected_result = mock_chat.title
        assert (
            Manager._chat_attribute_from_chat_id(
                custom_client=test_custom_client, chat_id=chat_id, attribute=attribute
            )
            == expected_result
        )
        return None


class TestChatEmoticonsFromChatId:
    @staticmethod
    @pytest.mark.parametrize(
        "chat_id, available_reactions, chat_is_private, expected_result",
        [
            (1, None, False, ()),
            (
                1,
                Mock(all_are_enabled=True, reactions=None),
                False,
                src.constants.VALID_EMOTICONS,
            ),
            (
                1,
                Mock(
                    all_are_enabled=False,
                    reactions=[Mock(emoji="👍"), Mock(emoji=None)],
                ),
                False,
                ("👍",),
            ),
            (1, None, True, src.constants.VALID_EMOTICONS),
        ],
    )
    def test(
        test_custom_client: CustomClient,
        chat_id: int,
        available_reactions: Any,
        chat_is_private: bool,
        expected_result: Sequence[str],
    ) -> None:
        manager = Manager()
        test_custom_client.chat_emoticons_map = {}
        with patch.object(
            manager, "_chat_attribute_from_chat_id", return_value=available_reactions
        ), patch.object(manager, "_is_chat_private", return_value=chat_is_private):
            result = manager._chat_emoticons_from_chat_id(test_custom_client, chat_id)
            assert result == expected_result
            assert test_custom_client.chat_emoticons_map[chat_id] == expected_result
        return None

    @staticmethod
    def test_with_emoticons_allowed(
        test_custom_client: CustomClient,
    ) -> None:
        manager = Manager()
        test_custom_client.chat_emoticons_map = {}
        emoticons_allowed = ["👍", "👎"]
        chat_id = 1
        test_custom_client.chat_emoticons_map[chat_id] = emoticons_allowed

        result = manager._chat_emoticons_from_chat_id(
            custom_client=test_custom_client, chat_id=chat_id
        )

        assert result == emoticons_allowed
        return None

    @staticmethod
    def test_with_no_reactions_and_not_private(
        test_custom_client: CustomClient,
    ) -> None:
        manager = Manager()
        test_custom_client.chat_emoticons_map = {}
        chat_id = 1

        with patch.object(
            manager, "_chat_attribute_from_chat_id", return_value=None
        ), patch.object(manager, "_is_chat_private", return_value=False):
            result = manager._chat_emoticons_from_chat_id(
                custom_client=test_custom_client, chat_id=chat_id
            )

        assert result == ()
        assert test_custom_client.chat_emoticons_map[chat_id] == ()
        return None

    @staticmethod
    def test_with_no_chat_reactions(
        test_custom_client: CustomClient,
    ) -> None:
        manager = Manager()
        test_custom_client.chat_emoticons_map = {}
        chat_id = 1

        available_reactions = Mock(all_are_enabled=False, reactions=None)

        with patch.object(
            manager, "_chat_attribute_from_chat_id", return_value=available_reactions
        ), patch.object(manager, "_is_chat_private", return_value=False):
            result = manager._chat_emoticons_from_chat_id(
                custom_client=test_custom_client, chat_id=chat_id
            )

        assert result == ()
        assert test_custom_client.chat_emoticons_map[chat_id] == ()
        return None


class TestSenderIsFriend:
    @staticmethod
    @pytest.mark.parametrize(
        "sender_info, expected_result",
        [
            (("Alice", src.constants.FriendshipStatus.FRIEND), True),
            (None, False),
        ],
    )
    def test(
        test_custom_client: CustomClient,
        sender_info: Optional[tuple],
        expected_result: bool,
    ) -> None:
        sender_id: int = 7
        test_custom_client.user_settings.targets = (
            {sender_id: sender_info} if sender_info else {}
        )
        assert (
            Manager._sender_is_friend(
                custom_client=test_custom_client, sender_id=sender_id
            )
            is expected_result
        )
        return None


class TestEmoticonsFromFriendship:
    @staticmethod
    def test(test_custom_client: CustomClient) -> None:
        is_friend = True
        test_custom_client.user_settings.emoticons_for_friends = ("👍",)
        assert Manager._emoticons_from_friendship(
            test_custom_client, is_friend=is_friend
        ) == ("👍",)
        return None


class TestConvertEmoticonsToEmojis:
    @staticmethod
    @pytest.mark.parametrize(
        "emoticons, expected_result",
        [
            (
                ["👍", "👎"],
                [ReactionEmoji(emoticon="👍"), ReactionEmoji(emoticon="👎")],
            ),
            ([], []),
            (
                ["👍", "👎", "invalid"],
                [ReactionEmoji(emoticon="👍"), ReactionEmoji(emoticon="👎")],
            ),
            (["invalid1", "invalid2"], []),
        ],
    )
    def test(
        emoticons: Sequence[str], expected_result: Sequence[ReactionEmoji]
    ) -> None:
        assert (
            Manager._convert_emoticons_to_emojis(emoticons=emoticons) == expected_result
        )
        return None


class TestConvertEmojisToEmoticons:
    @staticmethod
    @pytest.mark.parametrize(
        "emojis, expected_result",
        [
            (
                [ReactionEmoji(emoticon="👍"), ReactionEmoji(emoticon="👎")],
                ["👍", "👎"],
            ),
            ([], []),
            (
                [
                    ReactionEmoji(emoticon="👍"),
                    ReactionEmoji(emoticon=""),
                    ReactionEmoji(emoticon="👎"),
                ],
                ["👍", "👎"],
            ),
        ],
    )
    def test(emojis: Sequence[ReactionEmoji], expected_result: Sequence[str]) -> None:
        assert Manager._convert_emojis_to_emoticons(emojis=emojis) == expected_result
        return None


class TestWriteChatPeerFromId:
    @staticmethod
    @pytest.mark.asyncio
    async def test(test_custom_client: CustomClient, mock_peer: Peer) -> None:
        test_custom_client.resolve_peer = AsyncMock()  # type: ignore
        test_custom_client.resolve_peer.return_value = mock_peer
        chat_id: int = 1
        manager: Manager = Manager()
        await manager._write_chat_peer_from_id(
            custom_client=test_custom_client, chat_id=chat_id
        )
        test_custom_client.resolve_peer.assert_called_once_with(peer_id=chat_id)
        assert test_custom_client.chat_peer_map.get(chat_id) == mock_peer
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_key_error(
        test_custom_client: CustomClient,
    ) -> None:
        test_custom_client.resolve_peer = (  # type: ignore
            AsyncMock(side_effect=KeyError)
        )
        manager: Manager = Manager()
        chat_id: int = 1
        await manager._write_chat_peer_from_id(
            custom_client=test_custom_client, chat_id=chat_id
        )
        test_custom_client.resolve_peer.assert_called_once_with(peer_id=chat_id)
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_with_existing_peer(
        test_custom_client: CustomClient, mock_peer: Peer
    ) -> None:
        test_custom_client.resolve_peer = AsyncMock()  # type: ignore
        test_custom_client.resolve_peer.return_value = mock_peer
        chat_id: int = 1
        test_custom_client.chat_peer_map[chat_id] = mock_peer
        manager: Manager = Manager()
        await manager._write_chat_peer_from_id(
            custom_client=test_custom_client, chat_id=chat_id
        )
        test_custom_client.resolve_peer.assert_not_awaited()
        return None


class TestPeerFromChatId:
    @staticmethod
    def test(test_custom_client: CustomClient, mock_peer: Peer) -> None:
        chat_id: int = 1
        test_custom_client.chat_peer_map[chat_id] = mock_peer
        assert (
            Manager._peer_from_chat_id(
                custom_client=test_custom_client, chat_id=chat_id
            )
            == mock_peer
        )
        return None


class TestPlaceEmojis:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "side_effect, exception_to_raise, handler",
        [
            (None, None, None),  # Success case
            ([FloodWait(10), None], None, FloodWaitManager.handle),  # FloodWait case
            (ReactionInvalid(), ReactionInvalid, None),  # ReactionInvalid case
            (MessageNotModified(), MessageNotModified, None),  # MessageNotModified case
            (MessageIdInvalid(), MessageIdInvalid, None),  # MessageIdInvalid case
            (BadRequest(), BadRequest, None),  # BadRequest case
            (NotAcceptable(), NotAcceptable, None),  # NotAcceptable case
        ],
    )
    async def test(
        test_custom_client: CustomClient,
        mock_peer: Peer,
        one_emoticon: Sequence[str],
        side_effect: Sequence[Exception] | Exception | None,
        exception_to_raise: type[Exception] | None,
        handler: Optional[Callable],
    ) -> None:
        manager: Manager = Manager()
        custom_client: CustomClient = test_custom_client
        peer: Peer = mock_peer
        chat_id: int = 123
        message_id: int = 456
        emojis: Sequence[ReactionEmoji] = [ReactionEmoji(emoticon=one_emoticon[0])]

        custom_client.invoke = AsyncMock(side_effect=side_effect)  # type: ignore

        if handler:  # type: ignore
            with patch.object(
                FloodWaitManager, "handle", new_callable=AsyncMock
            ) as mock_handle:
                await manager._place_emojis(
                    custom_client, peer, chat_id, message_id, emojis
                )
                mock_handle.assert_called_once()
            assert custom_client.invoke.call_count == 2
        elif exception_to_raise:
            with pytest.raises(exception_to_raise):
                await manager._place_emojis(
                    custom_client, peer, chat_id, message_id, emojis
                )
        else:
            await manager._place_emojis(
                custom_client, peer, chat_id, message_id, emojis
            )
            custom_client.invoke.assert_called_once_with(
                functions.messages.SendReaction(
                    peer=peer,  # type: ignore
                    msg_id=message_id,
                    add_to_recent=True,
                    reaction=emojis,  # type: ignore
                )
            )
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_message_id_invalid(
        test_custom_client: CustomClient, mock_peer: Peer, one_emoticon: Sequence[str]
    ) -> None:
        manager: Manager = Manager()
        custom_client: CustomClient = test_custom_client
        peer: Peer = mock_peer
        chat_id: int = 123
        message_id: int = 456
        emojis: Sequence[ReactionEmoji] = [ReactionEmoji(emoticon=one_emoticon[0])]

        custom_client.invoke = AsyncMock(side_effect=MessageIdInvalid())  # type: ignore
        custom_client.msg_queue = deque([(chat_id, message_id)])
        custom_client.msg_keeper = LRUCache(
            maxsize=custom_client.user_settings.msg_queue_size
        )
        custom_client.msg_keeper[(chat_id, message_id)] = "some_value"

        with pytest.raises(MessageIdInvalid):
            await manager._place_emojis(
                custom_client, peer, chat_id, message_id, emojis
            )

        assert (chat_id, message_id) not in custom_client.msg_queue
        assert custom_client.msg_keeper.pop((chat_id, message_id), None) is None
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_floodwait(
        test_custom_client: CustomClient, mock_peer: Peer, one_emoticon: Sequence[str]
    ) -> None:
        manager: Manager = Manager()
        custom_client: CustomClient = test_custom_client
        peer: Peer = mock_peer
        chat_id: int = 123
        message_id: int = 456
        emojis: Sequence[ReactionEmoji] = [ReactionEmoji(emoticon=one_emoticon[0])]

        custom_client.invoke = (  # type: ignore
            AsyncMock(side_effect=[FloodWait(10), None])
        )

        with patch.object(
            FloodWaitManager, "handle", new_callable=AsyncMock
        ) as mock_handle:
            await manager._place_emojis(
                custom_client, peer, chat_id, message_id, emojis
            )

        mock_handle.assert_called_once()
        assert custom_client.invoke.call_count == 2
        return None


class TestSenderNameFromMessage:
    @staticmethod
    @pytest.mark.parametrize(
        "message, expected_result",
        [
            (None, None),
            (
                Message(
                    id=3,
                    chat=Chat(id=1, type=ChatType.PRIVATE),
                    from_user=User(
                        id=1, is_bot=False, first_name="John", last_name="Doe"
                    ),
                ),
                "John Doe",
            ),
            (
                Message(
                    id=3,
                    chat=Chat(id=1, type=ChatType.PRIVATE),
                    from_user=User(id=1, is_bot=False, first_name="John", last_name=""),
                ),
                "John",
            ),
            (
                Message(
                    id=3,
                    chat=Chat(id=1, type=ChatType.PRIVATE),
                    from_user=User(id=1, is_bot=False, first_name="", last_name="Doe"),
                ),
                "Doe",
            ),
            (
                Message(
                    id=3,
                    chat=Chat(id=1, type=ChatType.PRIVATE),
                    from_user=User(id=1, is_bot=False, first_name="", last_name=""),
                ),
                "No Name",
            ),
        ],
    )
    def test(message: Message, expected_result: str) -> None:
        assert Manager._sender_name_from_message(message) == expected_result
        return None


class TestChatTitleFromChatId:
    @staticmethod
    @pytest.mark.parametrize(
        "chat_id, chat_is_private, chat_title, first_name, last_name, expected_result",
        [
            (1, False, "Test Chat", "", "", "Test Chat"),
            (1, True, "", "John", "Doe", "John Doe"),
            (1, True, "", "John", "", "John"),
            (1, True, "", "", "Doe", "Doe"),
            (1, True, "", "", "", "No Name"),
        ],
    )
    def test(
        test_custom_client: CustomClient,
        chat_id: int,
        chat_is_private: bool,
        chat_title: str,
        first_name: str,
        last_name: str,
        expected_result: str,
    ) -> None:
        manager: Manager = Manager()

        def side_effect(custom_client, chat_id, attribute):
            """
            First two parameters are necessary but ignored
            """
            if attribute == "title":
                return chat_title
            elif attribute == "first_name":
                return first_name
            elif attribute == "last_name":
                return last_name

        with patch.object(
            manager, "_is_chat_private", return_value=chat_is_private
        ), patch.object(
            manager, "_chat_attribute_from_chat_id", side_effect=side_effect
        ):
            result = manager._chat_title_from_chat_id(test_custom_client, chat_id)
            assert result == expected_result

        return None


class TestLogMethodSuccess:
    @staticmethod
    @pytest.mark.parametrize(
        "message_attrs, chat_id, chat_title, recipient_name, "
        "picked_response_emoticons, expected_log_msg",
        [
            (
                {"id": 3, "link": "http://t.me/mocklink/3"},
                1,
                "Test Chat",
                "John Doe",
                ["👍", "👎"],
                "respond|John Doe|Test Chat|👍👎|http://t.me/mocklink/3",
            ),
            (
                {"id": 3, "link": ""},
                1,
                "Test Chat",
                "John Doe",
                ["👍"],
                "respond|John Doe|Test Chat|👍|NoURL",
            ),
            (
                {"id": 3, "link": "http://t.me/mocklink/3"},
                1,
                "Test Chat",
                "John",
                ["👍", "❤"],
                "respond|John|Test Chat|👍❤|http://t.me/mocklink/3",
            ),
            (
                {"id": 3, "link": "http://t.me/mocklink/3"},
                1,
                "Test Chat",
                "No Name",
                ["👍"],
                "respond|No Name|Test Chat|👍|http://t.me/mocklink/3",
            ),
        ],
    )
    def test(
        message_attrs: dict,
        chat_id: int,
        chat_title: str,
        recipient_name: str,
        picked_response_emoticons: Sequence[str],
        expected_log_msg: str,
        test_custom_client: CustomClient,
    ) -> None:
        manager: Manager = Manager()
        manager._chat_id_from_msg = Mock(return_value=chat_id)  # type: ignore
        manager._chat_title_from_chat_id = Mock(return_value=chat_title)  # type: ignore
        manager._sender_name_from_message = (  # type: ignore
            Mock(return_value=recipient_name)
        )

        message: Mock = Mock(spec=Message)
        for attr, value in message_attrs.items():
            setattr(message, attr, value)

        with patch("src.loggers.logger.success") as mock_success_logger:
            manager._log_method_success(
                method_name="respond",
                custom_client=test_custom_client,
                message=message,
                picked_response_emoticons=picked_response_emoticons,
            )
            mock_success_logger.assert_called_once_with(expected_log_msg)
        return None

    @staticmethod
    @pytest.mark.parametrize(
        "message_attrs, chat_id",
        [
            ({"id": 3, "link": None}, 1),
            ({"id": 3, "link": "http://t.me/mocklink/3"}, None),
        ],
    )
    def test_fail(
        message_attrs: dict,
        chat_id: int,
        test_custom_client: CustomClient,
    ) -> None:
        manager: Manager = Manager()
        manager._chat_id_from_msg = Mock(return_value=chat_id)  # type: ignore

        message: Mock = Mock(spec=Message)
        for attr, value in message_attrs.items():
            setattr(message, attr, value)

        with patch("src.loggers.logger.error") as mock_error_logger:
            manager._log_method_success(
                method_name="respond",
                custom_client=test_custom_client,
                message=message,
                picked_response_emoticons=["👍"],
            )
            mock_error_logger.assert_called_once()
        return None


class TestGetRandomMsgFromQueue:
    @staticmethod
    @pytest.mark.parametrize(
        "msg_queue, msg_keeper, msg_queue_container, expected_result",
        [
            # Empty message queue
            ([], {}, None, None),
            # Message in keeper
            ([(1,)], {(1,): Message(id=1)}, (1,), Message(id=1)),
            # Message not in keeper, but obtained from client
            ([(1,)], {}, (1,), Message(id=1)),
            # Message not in keeper and not obtained from client
            ([(1,)], {}, (1,), None),
        ],
    )
    @pytest.mark.asyncio
    async def test(
        msg_queue,
        msg_keeper,
        msg_queue_container,
        expected_result,
        test_custom_client: CustomClient,
    ) -> None:
        manager: Manager = Manager()
        test_custom_client.msg_queue = msg_queue
        test_custom_client.msg_keeper.update(msg_keeper)

        with patch("random.choice", return_value=msg_queue_container):
            if expected_result is None and msg_queue_container is not None:
                manager._get_message_from_client = (  # type: ignore
                    AsyncMock(return_value=None)
                )
            elif expected_result is not None and msg_queue_container is not None:
                manager._get_message_from_client = (  # type: ignore
                    AsyncMock(return_value=expected_result)
                )
            result = await manager._get_random_msg_from_queue(
                custom_client=test_custom_client
            )
            assert result == expected_result
            if expected_result is not None:
                assert (
                    test_custom_client.msg_keeper.get(msg_queue_container)
                    == expected_result
                )
        return None


class TestGetMessageFromClient:
    @staticmethod
    @pytest.mark.parametrize(
        "return_value, expected_result",
        [
            (Message(id=1), Message(id=1)),  # Single message
            ([Message(id=1), Message(id=2)], None),  # List of messages
        ],
    )
    @pytest.mark.asyncio
    async def test(
        return_value, expected_result, test_custom_client: CustomClient
    ) -> None:
        manager: Manager = Manager()
        msg_queue_container = (1,)

        with patch.object(
            test_custom_client, "get_messages", AsyncMock(return_value=return_value)
        ):
            result = await manager._get_message_from_client(
                test_custom_client, msg_queue_container
            )
            assert result == expected_result
        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_flood_wait(
        test_custom_client: CustomClient,
    ) -> None:
        manager: Manager = Manager()
        msg_queue_container = (1,)
        flood_wait_exception = FloodWait(10)

        with patch.object(
            test_custom_client,
            "get_messages",
            AsyncMock(side_effect=[flood_wait_exception, Message(id=1)]),
        ):
            with patch.object(FloodWaitManager, "handle", AsyncMock()) as mock_handle:
                result = await manager._get_message_from_client(
                    test_custom_client, msg_queue_container
                )
                assert result is not None
                assert result == Message(id=1)
                mock_handle.assert_called_once_with(
                    flood_wait_exception, custom_client=test_custom_client
                )
        return None


class TestGenerateDifferentEmoticons:
    @staticmethod
    @pytest.mark.parametrize(
        "msg_emoticons, response_emoticons, picker_results, "
        "expected_result, error_expected",
        [
            # No emoticon picker
            (["👍"], ["👎"], [], [], True),
            # Picker returns a different set
            (["👍"], ["👎"], [["👎"]], ["👎"], False),
            # Picker returns the same set, then a different set
            (["👍"], ["👍", "👎"], [["👍"], ["👎"]], ["👎"], False),
        ],
    )
    def test(
        msg_emoticons: Sequence[str],
        response_emoticons: Sequence[str],
        picker_results: Sequence[Sequence[Str]],
        expected_result: Sequence[str],
        error_expected: bool,
        test_custom_client: CustomClient,
    ) -> None:
        manager: Manager = Manager()

        if not picker_results:
            test_custom_client.emoticon_picker = None
        else:
            picker_mock: Mock = Mock(side_effect=picker_results)
            test_custom_client.emoticon_picker = picker_mock

        if error_expected:
            with pytest.raises(ValueError):
                manager._generate_different_emoticons(
                    test_custom_client, msg_emoticons, response_emoticons
                )
        else:
            result = manager._generate_different_emoticons(
                test_custom_client, msg_emoticons, response_emoticons
            )
            assert set(result) == set(expected_result)

            if picker_results:
                assert (
                    test_custom_client.emoticon_picker.call_count  # type: ignore
                    == len(picker_results)
                )
        return None


class TestMsgEmoticonsFromMsg:
    @staticmethod
    @pytest.mark.parametrize(
        "message, expected_result",
        [
            # Message is None
            (None, None),
            # Message has no reactions attribute
            (Mock(spec=Message, reactions=None), None),
            # Message has empty reactions
            (Mock(spec=Message, reactions=Mock(reactions=[])), ()),
            # Message has reactions with emojis
            (
                Mock(
                    spec=Message,
                    reactions=Mock(
                        reactions=[
                            Mock(spec=Reaction, emoji="👍"),
                            Mock(spec=Reaction, emoji="👎"),
                        ]
                    ),
                ),
                ("👍", "👎"),
            ),
            # Message has reactions, some without emojis
            (
                Mock(
                    spec=Message,
                    reactions=Mock(
                        reactions=[
                            Mock(spec=Reaction, emoji="👍"),
                            Mock(spec=Reaction, emoji=None),
                        ]
                    ),
                ),
                ("👍",),
            ),
        ],
    )
    def test(message: Message | None, expected_result: Sequence[str] | None) -> None:
        manager: Manager = Manager()
        result = manager._msg_emoticons_from_msg(message)
        assert result == expected_result
        return None


class TestUpdate:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "msg_queue, msg_keeper, random_msg, chat_id, emoticons_allowed,"
        "sender_id, response_emoticons, msg_emoticons,"
        "place_emojis_side_effect, should_log_success",
        [
            # Empty msg_queue
            (deque(), {}, None, None, None, None, None, None, None, False),
            # No message from queue
            (deque([(1,)]), {}, None, None, None, None, None, None, None, False),
            # No chat_id
            (
                deque([(1,)]),
                {},
                Mock(spec=Message),
                None,
                None,
                None,
                None,
                None,
                None,
                False,
            ),
            # Insufficient emoticons_allowed
            (
                deque([(1,)]),
                {},
                Mock(spec=Message),
                1,
                ["👍"],
                None,
                None,
                None,
                None,
                False,
            ),
            # No sender_id
            (
                deque([(1,)]),
                {},
                Mock(spec=Message),
                1,
                ["👍", "👎"],
                None,
                None,
                None,
                None,
                False,
            ),
            # No response_emoticons
            (
                deque([(1,)]),
                {},
                Mock(spec=Message),
                1,
                ["👍", "👎"],
                1,
                [],
                None,
                None,
                False,
            ),
            # No msg_emoticons
            (
                deque([(1,)]),
                {},
                Mock(spec=Message),
                1,
                ["👍", "👎"],
                1,
                ["👎"],
                None,
                None,
                False,
            ),
            # Same response_emoticons
            (
                deque([(1,)]),
                {},
                Mock(spec=Message),
                1,
                ["👍", "👎"],
                1,
                ["👎"],
                ["👎"],
                None,
                False,
            ),
            # Successful update
            (
                deque([(1,)]),
                {},
                Mock(spec=Message, id=1),
                1,
                ["👍", "👎"],
                1,
                ["👎"],
                ["👍"],
                None,
                True,
            ),
            # Place emojis exception
            (
                deque([(1,)]),
                {},
                Mock(spec=Message, id=1),
                1,
                ["👍", "👎"],
                1,
                ["👎"],
                ["👍"],
                BadRequest,
                False,
            ),
        ],
    )
    async def test(
        msg_queue: deque,
        msg_keeper: LRUCache,
        random_msg: Message | None,
        chat_id: int | None,
        emoticons_allowed: Sequence[str] | None,
        sender_id: int | None,
        response_emoticons: Sequence[str] | None,
        msg_emoticons: Sequence[str] | None,
        place_emojis_side_effect: Any,
        should_log_success: bool,
        test_custom_client: CustomClient,
    ) -> None:
        manager: Manager = Manager()

        test_custom_client.msg_queue = msg_queue
        test_custom_client.msg_keeper = msg_keeper

        manager._get_random_msg_from_queue = (  # type: ignore
            AsyncMock(return_value=random_msg)
        )
        manager._chat_id_from_msg = Mock(return_value=chat_id)  # type: ignore
        manager._chat_emoticons_from_chat_id = (  # type: ignore
            Mock(return_value=emoticons_allowed)
        )
        manager._sender_id_from_message = Mock(return_value=sender_id)  # type: ignore
        manager._get_response_emoticons = (  # type: ignore
            Mock(return_value=response_emoticons)
        )
        manager._msg_emoticons_from_msg = (  # type: ignore
            Mock(return_value=msg_emoticons)
        )
        manager._generate_different_emoticons = Mock(  # type: ignore
            return_value=["👎"] if msg_emoticons != response_emoticons else ["👍"]
        )
        manager._convert_emoticons_to_emojis = Mock(return_value=["👎"])  # type: ignore
        manager._peer_from_chat_id = Mock(return_value=Mock())  # type: ignore
        manager._place_emojis = (  # type: ignore
            AsyncMock(side_effect=place_emojis_side_effect)
        )
        manager._log_method_success = Mock()  # type: ignore

        await manager.update(test_custom_client)

        if place_emojis_side_effect:
            manager._place_emojis.assert_called_once()
            manager._log_method_success.assert_not_called()
        elif should_log_success:
            manager._place_emojis.assert_called_once()
            manager._log_method_success.assert_called_once()
        else:
            manager._place_emojis.assert_not_called()
            manager._log_method_success.assert_not_called()

        return None

    @staticmethod
    @pytest.mark.asyncio
    async def test_no_chat_peer(
        test_custom_client: CustomClient,
    ) -> None:
        manager = Manager()
        test_custom_client.msg_queue = deque([(1,)])
        mock_message = Mock(spec=Message)
        mock_message.id = 1

        with patch.object(
            manager, "_get_random_msg_from_queue", return_value=mock_message
        ), patch.object(manager, "_chat_id_from_msg", return_value=1), patch.object(
            manager, "_chat_emoticons_from_chat_id", return_value=["👍", "👎"]
        ), patch.object(
            manager, "_sender_id_from_message", return_value=1
        ), patch.object(
            manager, "_get_response_emoticons", return_value=["👍"]
        ), patch.object(
            manager, "_msg_emoticons_from_msg", return_value=["👎"]
        ), patch.object(
            manager, "_generate_different_emoticons", return_value=["👍"]
        ), patch.object(
            manager, "_convert_emoticons_to_emojis", return_value=["👍"]
        ), patch.object(
            manager, "_peer_from_chat_id", return_value=None
        ), patch.object(
            manager, "_place_emojis", new_callable=AsyncMock
        ) as mock_place_emojis:
            await manager.update(test_custom_client)
            mock_place_emojis.assert_not_called()
        return None
