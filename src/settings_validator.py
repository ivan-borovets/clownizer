import settings
from settings import logger
from context import Context


class SettingsException(Exception):
    pass


class SettingsValidator:
    @staticmethod
    def validate() -> None:
        """
        Validates application settings, needs a Telegram Premium status set in the ContextData
        """
        is_correct_user_status = {item.name for item in settings.FriendshipStatus} == {
            "FRIEND",
            "ENEMY",
        }
        is_enough_responses = (
            len(settings.EMOTICONS_FOR_FRIENDS) > (1, 3)[Context.is_premium]
            and len(settings.EMOTICONS_FOR_ENEMIES) > (1, 3)[Context.is_premium]
        )
        is_enough_targets = len(settings.TARGETS) > 0
        is_enough_memory = settings.MSG_QUEUE_SIZE > 0
        condition = all(
            (
                is_correct_user_status,
                is_enough_responses,
                is_enough_targets,
                is_enough_memory,
            )
        )
        if not condition:
            raise SettingsException("The program launch failed. Check the settings.py!")
        logger.success("The settings look fine, the program works...")
