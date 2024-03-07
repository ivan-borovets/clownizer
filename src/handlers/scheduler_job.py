from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

import settings
from context import Context


class SchedulerJobHandler:
    @staticmethod
    def add(scheduler: AsyncIOScheduler, func: callable, args=None) -> None:
        """
        Adds a job to the existing scheduler
        """
        if args is None:
            args = []
        trigger = IntervalTrigger(
            seconds=settings.UPDATE_TIMEOUT, jitter=settings.UPDATE_JITTER
        )
        scheduler.add_job(
            func,
            trigger=trigger,
            args=args,
            id="1",
            replace_existing=True,
        )

    @staticmethod
    def stop() -> None:
        """
        Stops all jobs in the existing scheduler
        """
        Context.current_scheduler.pause()

    @staticmethod
    def resume() -> None:
        """
        Resumes all jobs in the existing scheduler
        """
        Context.current_scheduler.resume()
