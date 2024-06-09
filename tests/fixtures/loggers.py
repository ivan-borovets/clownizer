from pathlib import Path
from typing import Callable, Generator

import pytest
from loguru import logger

from src.loggers import LoggerFilters


class MockLevel:
    def __init__(self, name):
        self.name = name


@pytest.fixture
def create_log_record() -> Callable:

    def _create_log_record(level_name: str) -> dict:
        return {"level": MockLevel(level_name)}

    return _create_log_record


@pytest.fixture
def setup_logger(tmp_path: Path) -> Generator[Path, None, None]:
    log_dir: Path = tmp_path / "logs"
    log_dir.mkdir()
    log_file: Path = log_dir / "test_logfile.log"

    logger.remove()
    logger.add(
        sink=log_file,
        format="{time:YYYY-MM-DD|HH:mm:ss}|{level}|{message}",
        filter=LoggerFilters.success_error_filter,  # type: ignore
        rotation="1 day",
        compression="zip",
    )
    yield log_file
