import pytest

import src.constants


@pytest.fixture
def valid_config_content() -> str:
    return """
---
api_id: 123456
api_hash: 12345a678b9c0d12ef123g45ef678g90
msg_queue_size: 10
update_timeout: 5
update_jitter: 2
chats_allowed: 
  "-12345": Test Chat Name
targets: 
  "123456789":
    - Alice
    - Enemy
emoticons_for_enemies:
  - 🤡
emoticons_for_friends:
  - 👍
"""


@pytest.fixture
def invalid_config_content() -> str:
    return """
---
api_id: string
api_hash: 12345a678b9c0d12ef123g45ef678g90
msg_queue_size: 10
update_timeout: 5
update_jitter: 2
chats_allowed: 
  "-12345": Test Chat Name
targets: 
  "123456789":
    - Alice
    - Enemy
emoticons_for_enemies:
  - 🤡
emoticons_for_friends:
  - 👍
"""


@pytest.fixture
def valid_config() -> dict:
    return {
        "api_id": 123456,
        "api_hash": "12345a678b9c0d12ef123g45ef678g90",
        "msg_queue_size": 10,
        "update_timeout": 5,
        "update_jitter": 2,
        "chats_allowed": {-12345: "Test Chat Name"},
        "targets": {123456789: ("Alice", src.constants.FriendshipStatus.ENEMY)},
        "emoticons_for_enemies": ("🤡",),
        "emoticons_for_friends": ("👍",),
    }
