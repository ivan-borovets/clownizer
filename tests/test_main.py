from unittest.mock import Mock, patch

from pyrogram.handlers import MessageHandler

from src.custom_client import CustomClient
from src.main import register_msg_handler, register_scheduler


def test_register_msg_handler(test_client_for_custom_client: CustomClient) -> None:
    mock_msg_handler: Mock = Mock()

    with patch.object(
        test_client_for_custom_client, "add_handler", autospec=True
    ) as mock_add_handler:
        register_msg_handler(
            custom_client=test_client_for_custom_client, func=mock_msg_handler
        )

    mock_add_handler.assert_called_once()
    args, _ = mock_add_handler.call_args
    handler = args[0]
    assert isinstance(handler, MessageHandler)
    return None


def test_register_scheduler(test_client_for_custom_client: CustomClient) -> None:
    mock_func: Mock = Mock()

    with patch.object(
        test_client_for_custom_client.scheduler, "add_job"
    ) as mock_add_job, patch.object(
        test_client_for_custom_client.scheduler, "start"
    ) as mock_start:

        register_scheduler(custom_client=test_client_for_custom_client, func=mock_func)

        mock_add_job.assert_called_once_with(
            func=mock_func,
            trigger=test_client_for_custom_client.scheduler.trigger,
            args=[test_client_for_custom_client],
            id=test_client_for_custom_client.name,
            replace_existing=True,
        )
        mock_start.assert_called_once()
    return None
