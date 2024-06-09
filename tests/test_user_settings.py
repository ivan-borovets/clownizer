from pathlib import Path
from typing import Sequence

import pytest
from pydantic import ValidationError

from src.user_settings import UserSettings

required_fields: list[str] = list(UserSettings.model_fields.keys())


def test_from_config_valid(
    valid_config_content: str, valid_config: dict, tmp_path: Path
) -> None:
    config_file: Path = tmp_path / "config.yaml"
    config_file.write_text(valid_config_content)

    settings: UserSettings = UserSettings.from_config(str(config_file))
    assert settings.api_id == valid_config["api_id"]
    assert settings.api_hash == valid_config["api_hash"]
    assert settings.msg_queue_size == valid_config["msg_queue_size"]
    assert settings.update_timeout == valid_config["update_timeout"]
    assert settings.update_jitter == valid_config["update_jitter"]
    assert settings.chats_allowed == valid_config["chats_allowed"]
    assert settings.targets == valid_config["targets"]
    assert settings.emoticons_for_enemies == valid_config["emoticons_for_enemies"]
    assert settings.emoticons_for_friends == valid_config["emoticons_for_friends"]
    return None


def test_from_config_invalid(invalid_config_content: str, tmp_path: Path) -> None:
    config_file: Path = tmp_path / "config.yaml"
    config_file.write_text(invalid_config_content)

    with pytest.raises(ValidationError):
        UserSettings.from_config(str(config_file))
    return None


def test_creation_valid(valid_config: dict) -> None:
    settings: UserSettings = UserSettings(**valid_config)  # type: ignore
    assert settings.api_id == valid_config["api_id"]
    assert settings.api_hash == valid_config["api_hash"]
    assert settings.msg_queue_size == valid_config["msg_queue_size"]
    assert settings.update_timeout == valid_config["update_timeout"]
    assert settings.update_jitter == valid_config["update_jitter"]
    assert settings.chats_allowed == valid_config["chats_allowed"]
    assert settings.targets == valid_config["targets"]
    assert settings.emoticons_for_enemies == valid_config["emoticons_for_enemies"]
    assert settings.emoticons_for_friends == valid_config["emoticons_for_friends"]
    return None


@pytest.mark.parametrize("missing_field", required_fields)
def test_missing_required_fields(valid_config: dict, missing_field: str) -> None:
    incomplete_config: dict = valid_config.copy()
    del incomplete_config[missing_field]
    with pytest.raises(ValidationError):
        UserSettings(**incomplete_config)  # type: ignore
    return None


@pytest.mark.parametrize(
    "invalid_data, expected_exception",
    [
        ({"msg_queue_size": 0}, ValidationError),
        ({"update_timeout": 1}, ValidationError),
        ({"update_jitter": -1}, ValidationError),
    ],
)
def test_invalid_cases(
    valid_config: dict,
    invalid_data: dict[str, int],
    expected_exception,
) -> None:
    invalid_config: dict = valid_config.copy()
    invalid_config.update(invalid_data)
    with pytest.raises(expected_exception):
        UserSettings(**invalid_config)  # type: ignore
    return None


@pytest.mark.parametrize(
    "field, invalid_value, expected_exception",
    [
        ("targets", {}, ValidationError),
        ("emoticons_for_enemies", (), ValidationError),
        ("emoticons_for_friends", (), ValidationError),
    ],
)
def test_empty_collections(
    valid_config: dict, field: str, invalid_value: Sequence, expected_exception
) -> None:
    invalid_config: dict = valid_config.copy()
    invalid_config[field] = invalid_value
    with pytest.raises(expected_exception):
        UserSettings(**invalid_config)  # type: ignore
    return None


@pytest.mark.parametrize("field", ["emoticons_for_enemies", "emoticons_for_friends"])
def test_invalid_emoticons(valid_config: dict, field: str) -> None:
    invalid_config: dict = valid_config.copy()
    invalid_config[field] = ("invalid str",)
    with pytest.raises(ValidationError):
        UserSettings(**invalid_config)  # type: ignore
    return None


def test_invalid_targets(valid_config: dict) -> None:
    invalid_config: dict = valid_config.copy()
    invalid_config["targets"] = {123456789: ("Alice", "Neutral")}
    with pytest.raises(ValidationError):
        UserSettings(**invalid_config)  # type: ignore
    return None
