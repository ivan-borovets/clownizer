from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.custom_scheduler import CustomScheduler
from tests.fixtures.custom_client import MockUserSettings


class TestCustomScheduler:
    @staticmethod
    def test_init(user_settings: MockUserSettings) -> None:
        scheduler: CustomScheduler = CustomScheduler(user_settings=user_settings)
        assert isinstance(scheduler, AsyncIOScheduler)
        assert isinstance(scheduler.trigger, IntervalTrigger)
        assert (
            scheduler.trigger.interval.total_seconds() == user_settings.update_timeout
        )
        assert scheduler.trigger.jitter == user_settings.update_jitter
        return None
