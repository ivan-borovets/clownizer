import yaml
from pydantic import BaseModel, ValidationError

from src.loggers import logger


class UserSettings(BaseModel):
    api_id: int
    api_hash: str

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
        else:
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
