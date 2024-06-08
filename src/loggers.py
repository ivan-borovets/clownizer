import os
import sys
from typing import Any

from loguru import logger

log_dir = os.getenv(key="LOG_DIR", default="logs/")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)  # pragma: no cover


class LoggerFilters:
    @staticmethod
    def _get_record_lvl_name(record: dict) -> Any:
        """
        Returns `record["level"].name`
        """
        level: Any = record.get("level", None)
        name: Any = getattr(level, "name", None)
        return name

    @classmethod
    def success_filter(
        cls,
        record: dict,
    ) -> bool:  # Record type from loguru can't be used for annotation
        """
        Filters Loguru Records by condition
        """
        record_lvl_name = cls._get_record_lvl_name(record=record)
        if record_lvl_name is None:
            return False

        return record_lvl_name == "SUCCESS"

    @classmethod
    def error_filter(
        cls,
        record: dict,
    ) -> bool:  # Record type from loguru can't be used for annotation
        """
        Filters Loguru Records by condition
        """
        record_lvl_name = cls._get_record_lvl_name(record=record)
        if record_lvl_name is None:
            return False

        return record_lvl_name == "ERROR"

    @classmethod
    def success_error_filter(
        cls,
        record: dict,
    ) -> bool:  # Record type from loguru can't be used for annotation
        """
        Filters Loguru Records by condition
        """
        record_lvl_name = cls._get_record_lvl_name(record=record)
        if record_lvl_name is None:
            return False

        return record_lvl_name in ("SUCCESS", "ERROR")


logger.remove()
logger.add(
    sink=sys.stderr,
    format=(
        "<blue>{time:YYYY-MM-DD|HH:mm:ss}|</blue>"
        "<green>{level}</green>"
        "<blue>|{message}</blue>"
    ),
    colorize=True,
    level="SUCCESS",
    filter=LoggerFilters.success_filter,  # type: ignore
)
logger.add(
    sink=sys.stderr,
    format=(
        "<yellow>{time:YYYY-MM-DD|HH:mm:ss}|</yellow>"
        "<red>{level}</red>"
        "<yellow>|{message}</yellow>"
    ),
    colorize=True,
    level="ERROR",
    filter=LoggerFilters.error_filter,  # type: ignore
)
logger.add(
    sink=f"{log_dir}/logfile_{{time:YYYY-MM-DD_HH-mm-ss}}.log",
    format="{time:YYYY-MM-DD|HH:mm:ss}|{level}|{message}",
    filter=LoggerFilters.success_error_filter,  # type: ignore
    rotation="1 day",
    compression="zip",
)
