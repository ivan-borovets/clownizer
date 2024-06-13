from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from pyrogram.errors import FloodWait

from src.custom_client import CustomClient
from src.floodwait_manager import FloodWaitManager


class TestFloodwaitManager:
    @staticmethod
    @pytest.mark.asyncio
    async def test_handle(
        flood_wait_error: FloodWait, test_custom_client: CustomClient
    ) -> None:
        client: CustomClient = test_custom_client
        client.scheduler.pause = Mock()
        client.scheduler.resume = Mock()

        with patch("src.floodwait_manager.logger.error") as mock_logger_error:
            start_time: datetime = datetime.now()
            await FloodWaitManager.handle(f=flood_wait_error, custom_client=client)
            end_time: datetime = start_time + timedelta(seconds=flood_wait_error.value)

        client.scheduler.pause.assert_called_once()
        client.scheduler.resume.assert_called_once()
        mock_logger_error.assert_called_once()

        logged_message: str = mock_logger_error.call_args[0][0]
        assert (
            f"FloodWait is provoked...|{flood_wait_error.value} s to wait"
            in logged_message
        )
        assert "Program will resume at" in logged_message

        logged_time_str: str = logged_message.split("Program will resume at ")[1]
        logged_time: datetime = datetime.strptime(logged_time_str, "%Y-%m-%d %H:%M:%S")
        assert abs((logged_time - end_time).total_seconds()) < 1
        return None
