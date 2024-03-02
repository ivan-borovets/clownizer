from enum import Enum


class UserStatus(Enum):
    FRIEND = "Friend"
    ENEMY = "Enemy"


# From this point on, the values can be changed
MESSAGE_MEMORY_SIZE = 10
REFRESH_SLEEP_TIME = (5, 10)

# Keep your enemies close
TARGETS = {
    # 123456789: ("John Doe", UserStatus.ENEMY),
    # 234567890: ("Tommy Atkins", UserStatus.ENEMY),

    # 345678901: ("Alice", UserStatus.FRIEND),
    # 456789012: ("Bob", UserStatus.FRIEND),
}

RESPONSE_TO_ENEMY = ('💩', '🖕', '🤮', '🤣', '🍌', '💊', '😐', '💅', '🦄', '👎',)
RESPONSE_TO_FRIEND = ('👍', '🔥', '🫡', '🤗', '⚡', '🤝', '😍', '🎉', '👏',)

# Don't try these, they are broken
# RESPONSES_BROKEN = ('️💯', '❤️',)
