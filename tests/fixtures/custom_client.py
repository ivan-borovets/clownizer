from typing import Sequence

import pytest

import src.constants
from src.custom_client import CustomClient
from src.user_settings import UserSettings


class MockUserSettings(UserSettings):
    api_id: int = 123456
    api_hash: str = "12345a678b9c0d12ef123g45ef678g90"
    msg_queue_size: int = 10
    update_timeout: int = 5
    update_jitter: int = 2
    chats_allowed: dict[int, str] = {-12345: "Test Chat Name"}
    targets: dict[int, tuple[str, src.constants.FriendshipStatus]] = {
        123456789: ("Alice", src.constants.FriendshipStatus.ENEMY)
    }
    emoticons_for_enemies: tuple[str, ...] = ("🤡",)
    emoticons_for_friends: tuple[str, ...] = ("👍",)


@pytest.fixture
def user_settings() -> MockUserSettings:
    return MockUserSettings()


@pytest.fixture
def test_client_for_custom_client() -> CustomClient:
    user_settings: MockUserSettings = MockUserSettings()
    client: CustomClient = CustomClient(
        name="test_client", user_settings=user_settings  # type: ignore
    )
    return client


@pytest.fixture
def many_emoticons() -> Sequence[str]:
    return [
        "👍",
        "👎",
        "❤",
        "🔥",
        "🥰",
    ]


@pytest.fixture
def three_emoticons() -> Sequence[str]:
    return [
        "👍",
        "👎",
        "❤",
    ]


@pytest.fixture
def two_emoticons() -> Sequence[str]:
    return [
        "👍",
        "👎",
    ]


@pytest.fixture
def one_emoticon() -> Sequence[str]:
    return ["👍"]


@pytest.fixture
def no_emoticons() -> Sequence[str]:
    return []
