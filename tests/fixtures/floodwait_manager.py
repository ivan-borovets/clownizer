import pytest
from pyrogram.errors import FloodWait


@pytest.fixture
def flood_wait_error() -> FloodWait:
    return FloodWait(value=1)
