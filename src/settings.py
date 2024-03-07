import sys
from enum import Enum
from loguru import logger


class FriendshipStatus(Enum):
    FRIEND = "Friend"
    ENEMY = "Enemy"


# From this point on, the values can be changed
MSG_QUEUE_SIZE = 10
UPDATE_TIMEOUT = 3
UPDATE_JITTER = 2

# Keep your enemies close
TARGETS = {
    # 123456789: ("John Doe", FriendshipStatus.ENEMY),
    # 234567890: ("Tommy Atkins", FriendshipStatus.ENEMY),
    # 345678901: ("Alice", FriendshipStatus.FRIEND),
    # 456789012: ("Bob", FriendshipStatus.FRIEND),
}

EMOTICONS_FOR_ENEMIES = (
    "🤡",
    "💩",
    "🖕",
    "🤮",
    "🤣",
    "🍌",
    "💊",
    "🌭",
    "😐",
    "💅",
    "🦄",
    "👎",
    "🗿",
    "🆒",
)
EMOTICONS_FOR_FRIENDS = (
    "👍",
    "❤️",
    "🔥",
    "🫡",
    "💯",
    "🤗",
    "⚡",
    "🤝",
    "😍",
    "🎉",
    "👏",
)

# Don't try these, they are broken
# RESPONSES_BROKEN = (
#     "⛄️",
#     "🎅",
# )
# SOMETIMES_BROKEN = ("❤️",)

EMOTICONS_BY_FRIENDSHIP = (EMOTICONS_FOR_FRIENDS, EMOTICONS_FOR_ENEMIES)


# Don't touch this, if you aren't sure
class Logger:

    @staticmethod
    def success_filter(
            record: dict,
    ) -> bool:  # Record type from loguru can't be used for annotation
        """
        Filters Loguru Records by condition
        """
        return record["level"].name == "SUCCESS"

    @staticmethod
    def error_filter(
            record: dict,
    ) -> bool:  # Record type from loguru can't be used for annotation
        """
        Filters Loguru Records by condition
        """
        return record["level"].name == "ERROR"

    @staticmethod
    def success_error_filter(
            record: dict,
    ) -> bool:  # Record type from loguru can't be used for annotation
        """
        Filters Loguru Records by condition
        """
        return record["level"].name in ("SUCCESS", "ERROR")


logger.remove()
logger.add(
    sink=sys.stderr,
    format="<blue>{time:YYYY-MM-DD|HH:mm:ss}|</blue><green>{level}</green><blue>|{message}</blue>",
    colorize=True,
    level="SUCCESS",
    filter=Logger.success_filter,
)
logger.add(
    sink=sys.stderr,
    format="<yellow>{time:YYYY-MM-DD|HH:mm:ss}|</yellow><red>{level}</red><yellow>|{message}</yellow>",
    colorize=True,
    level="ERROR",
    filter=Logger.error_filter,
)
logger.add(
    sink="../logs/logfile_{time:YYYY-MM-DD_HH-mm-ss}.log",
    format="{time:YYYY-MM-DD|HH:mm:ss}|{level}|{message}",
    filter=Logger.success_error_filter,
    rotation="1 day",
    compression="zip",
)
