import os
import sys

from loguru import logger

log_dir = os.getenv(key="LOG_DIR", default="logs/")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)


class LoggerFilters:
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
