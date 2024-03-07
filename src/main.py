from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client, idle
from pyrogram.handlers import MessageHandler
from context import Context

from handlers.emoji import EmojiHandler
from handlers.scheduler_job import SchedulerJobHandler
from settings_validator import SettingsValidator


async def main():
    async with Context.app as app:
        app: Client
        await Context.set_emoticon_picker(app)
        SettingsValidator.validate()
        app.add_handler(MessageHandler(EmojiHandler.respond))
        Context.current_scheduler = AsyncIOScheduler()
        SchedulerJobHandler.add(
            scheduler=Context.current_scheduler,
            func=EmojiHandler.update,
            args=[
                Context.app,
            ],
        )
        Context.current_scheduler.start()
        await idle()


Context.app.run(main())
