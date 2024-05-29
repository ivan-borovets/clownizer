import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

import constants
from loggers import logger


class UserSettings(BaseModel):
    api_id: int
    api_hash: str
    msg_queue_size: int = Field(default=..., ge=1)
    update_timeout: int = Field(default=..., ge=2)
    update_jitter: int = Field(default=..., ge=0)
    chats_allowed: dict[int, str] | None
    targets: dict[int, tuple[str, constants.FriendshipStatus]]
    emoticons_for_enemies: tuple[str, ...]
    emoticons_for_friends: tuple[str, ...]

    @classmethod
    def from_config(cls, config_file: str) -> "UserSettings":
        """
        Validates config and returns UserSettings instance
        """
        try:
            dict_config = cls._dict_from_yaml(config_file)
            user_settings = cls(**dict_config)
        except ValidationError:
            logger.error("The program launch failed. Check the config.yaml!")
            raise
        logger.success("The settings look fine!")
        return user_settings

    @staticmethod
    def _dict_from_yaml(yaml_file: str) -> dict:
        """
        Returns dict with YAML data
        """
        with open(file=yaml_file, mode="r", encoding="utf-8") as file:
            yaml_dict = yaml.safe_load(file)
        return yaml_dict

    # pylint: disable=E0213
    @field_validator("emoticons_for_enemies")
    def validate_enemy_emo(cls, v):
        for emoticon in v:
            if emoticon not in constants.VALID_EMOTICONS:
                raise ValueError(f"{emoticon} in `emoticons_for_enemies` is not valid!")
        return v

    # pylint: disable=E0213
    @field_validator("emoticons_for_friends")
    def validate_friend_emo(cls, v):
        for emoticon in v:
            if emoticon not in constants.VALID_EMOTICONS:
                raise ValueError(f"{emoticon} in `emoticons_for_friends` is not valid!")
        return v

    # pylint: disable=E0213
    @field_validator("targets", "emoticons_for_enemies", "emoticons_for_friends")
    def validate_length(cls, v):
        if len(v) == 0:
            raise ValueError(
                "The length of the `targets` and `emoticons` should be greater than 0!"
            )
        return v
