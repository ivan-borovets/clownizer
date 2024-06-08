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
def test_success_filter(create_log_record, level_name, expected) -> None:
    if level_name is not None:
        record = create_log_record(level_name)
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
def test_error_filter(create_log_record, level_name, expected) -> None:
    if level_name is not None:
        record = create_log_record(level_name)
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
def test_success_error_filter(create_log_record, level_name, expected) -> None:
    if level_name is not None:
        record = create_log_record(level_name)
    else:
        record = {"level": None}
    assert LoggerFilters.success_error_filter(record=record) is expected
    return None


def test_success_logging(setup_logger) -> None:
    log_file = setup_logger
    logger.success("Test success message")

    with open(log_file, "r") as f:
        logs = f.read()

    assert "SUCCESS" in logs
    assert "Test success message" in logs
    return None


def test_error_logging(setup_logger) -> None:
    log_file = setup_logger
    logger.error("Test error message")

    with open(log_file, "r") as f:
        logs = f.read()

    assert "ERROR" in logs
    assert "Test error message" in logs
    return None


def test_info_logging_not_logged(setup_logger) -> None:
    log_file = setup_logger
    logger.info("Test info message")

    with open(log_file, "r") as f:
        logs = f.read()

    assert "INFO" not in logs
    assert "Test info message" not in logs
    return None


def test_warning_logging_not_logged(setup_logger) -> None:
    log_file = setup_logger
    logger.warning("Test warning message")

    with open(log_file, "r") as f:
        logs = f.read()

    assert "WARNING" not in logs
    assert "Test warning message" not in logs
    return None


def test_logging_with_filters(setup_logger):
    log_file = setup_logger
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
