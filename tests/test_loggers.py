from pathlib import Path
from typing import Callable

import pytest
from loguru import logger

from src.loggers import LoggerFilters


@pytest.mark.parametrize(
    "level_name, expected",
    [
        ("SUCCESS", True),
        ("ERROR", False),
        (None, False),
        ("INFO", False),
        ("DEBUG", False),
    ],
)
def test_success_filter(
    create_log_record: Callable, level_name: str | None, expected: bool
) -> None:
    if level_name is not None:
        record: dict = create_log_record(level_name)
    else:
        record = {"level": None}
    assert LoggerFilters.success_filter(record=record) is expected
    return None


@pytest.mark.parametrize(
    "level_name, expected",
    [
        ("SUCCESS", False),
        ("ERROR", True),
        (None, False),
        ("INFO", False),
        ("DEBUG", False),
    ],
)
def test_error_filter(
    create_log_record: Callable, level_name: str | None, expected: bool
) -> None:
    if level_name is not None:
        record: dict = create_log_record(level_name)
    else:
        record = {"level": None}
    assert LoggerFilters.error_filter(record=record) is expected
    return None


@pytest.mark.parametrize(
    "level_name, expected",
    [
        ("SUCCESS", True),
        ("ERROR", True),
        (None, False),
        ("INFO", False),
        ("DEBUG", False),
    ],
)
def test_success_error_filter(
    create_log_record: Callable, level_name: str | None, expected: bool
) -> None:
    if level_name is not None:
        record: dict = create_log_record(level_name)
    else:
        record = {"level": None}
    assert LoggerFilters.success_error_filter(record=record) is expected
    return None


@pytest.mark.parametrize(
    "log_method, log_message, log_level, should_be_logged",
    [
        (logger.success, "Test success message", "SUCCESS", True),
        (logger.error, "Test error message", "ERROR", True),
        (logger.info, "Test info message", "INFO", False),
        (logger.warning, "Test warning message", "WARNING", False),
    ],
)
def test_logging(
    setup_logger: Path,
    log_method: Callable,
    log_message: str,
    log_level: str,
    should_be_logged: bool,
) -> None:
    log_file: Path = setup_logger
    log_method(log_message)

    with open(log_file, "r") as f:
        logs = f.read()

    if should_be_logged:
        assert log_level in logs
        assert log_message in logs
    else:
        assert log_level not in logs
        assert log_message not in logs
    return None


def test_logging_with_filters(setup_logger: Path):
    log_file: Path = setup_logger
    logger.success("Success msg 1")
    logger.error("Error msg 1")
    logger.debug("Debug msg 1")
    logger.warning("Warning msg 1")
    logger.info("Info msg 1")
    logger.success("Success msg 2")
    logger.error("Error msg 2")

    with open(log_file, "r") as f:
        logs = f.read()

    assert "Success msg 1" in logs
    assert "Error msg 1" in logs
    assert "Debug msg 1" not in logs
    assert "Warning msg 1" not in logs
    assert "Info msg 1" not in logs
    assert "Success msg 2" in logs
    assert "Error msg 2" in logs
