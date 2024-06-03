from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.user_settings import UserSettings


class CustomScheduler(AsyncIOScheduler):
    def __init__(self, user_settings: UserSettings, **options):
        super().__init__(**options)
        self.trigger = IntervalTrigger(
            seconds=user_settings.update_timeout,
            jitter=user_settings.update_jitter,
        )
