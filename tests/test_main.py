from unittest.mock import Mock, patch

from pyrogram.handlers import MessageHandler

from src.custom_client import CustomClient
from src.main import register_msg_handler, register_scheduler


class TestRegister:
    @staticmethod
    def test_msg_handler(test_custom_client: CustomClient) -> None:
        mock_msg_handler: Mock = Mock()

        with patch.object(
            test_custom_client, "add_handler", autospec=True
        ) as mock_add_handler:
            register_msg_handler(
                custom_client=test_custom_client, func=mock_msg_handler
            )

        mock_add_handler.assert_called_once()
        args, _ = mock_add_handler.call_args
        handler = args[0]
        assert isinstance(handler, MessageHandler)
        return None

    @staticmethod
    def test_scheduler(test_custom_client: CustomClient) -> None:
        mock_func: Mock = Mock()

        with patch.object(
            test_custom_client.scheduler, "add_job"
        ) as mock_add_job, patch.object(
            test_custom_client.scheduler, "start"
        ) as mock_start:
            register_scheduler(custom_client=test_custom_client, func=mock_func)

            mock_add_job.assert_called_once_with(
                func=mock_func,
                trigger=test_custom_client.scheduler.trigger,
                args=[test_custom_client],
                id=test_custom_client.name,
                replace_existing=True,
            )
            mock_start.assert_called_once()
        return None
