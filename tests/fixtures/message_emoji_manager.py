from unittest.mock import create_autospec

import pytest
from pyrogram.raw.base import Peer
from pyrogram.types import Chat, Message, User
from pyrogram.types.messages_and_media.message import Str


@pytest.fixture
def mock_chat() -> Chat:
    mock_chat: Chat = create_autospec(Chat, instance=True)
    mock_chat.id = 1
    return mock_chat


@pytest.fixture
def mock_user() -> User:
    mock_user: User = create_autospec(User, instance=True)
    mock_user.id = 2
    mock_user.is_bot = False
    mock_user.first_name = "First"
    mock_user.last_name = "Last"
    return mock_user


@pytest.fixture
def mock_message(mock_chat: Chat, mock_user: User) -> Message:
    mock_message: Message = create_autospec(Message, instance=True)
    mock_message.id = 3
    mock_message.chat = mock_chat
    mock_message.from_user = mock_user
    mock_message.text = Str("Hello, world!")

    return mock_message


@pytest.fixture
def mock_peer() -> Peer:
    mock_peer: Peer = create_autospec(Peer, instance=True)
    return mock_peer
