import asyncio
import os
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from collections import deque
from dotenv import load_dotenv
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.raw.types import ReactionEmoji

import const

load_dotenv()
app = Client(name="my_account",
             api_id=os.getenv('API_ID'),
             api_hash=os.getenv('API_HASH'), )


class ContextData:
    is_premium = None
    response_method = None
    current_responses = None
    last_messages = deque(maxlen=const.MESSAGE_MEMORY_SIZE)

    @classmethod
    async def check_premium(cls, client: Client):
        user = await client.get_me()
        cls.is_premium = user.is_premium


class ResponseMethods:
    @staticmethod
    def choice_method(responses):
        return random.choice(responses)

    @staticmethod
    def sample_method(responses):
        return random.sample(responses, k=min(3, len(responses)))

    @classmethod
    async def send_response(cls, client: Client, message: Message, responses):
        if ContextData.is_premium is None:
            raise Exception("Premium Status is Unknown!")
        response_method = (cls.choice_method,
                           cls.sample_method)[ContextData.is_premium]
        random_responses = response_method(responses)
        await client.invoke(
            functions.messages.SendReaction(
                peer=await client.resolve_peer(message.chat.id),
                msg_id=message.id,
                add_to_recent=True,
                reaction=[ReactionEmoji(emoticon=response) for response in random_responses]
            )
        )


class ResponseHandler:
    @staticmethod
    async def message_handler(client: Client, message: Message):
        responses = ()
        if message is not None and message.from_user is not None:
            target = const.TARGETS.get(message.from_user.id, ())
            if target:
                _, status = target
                if status == const.UserStatus.ENEMY:
                    responses = const.RESPONSE_TO_ENEMY
                elif status == const.UserStatus.FRIEND:
                    responses = const.RESPONSE_TO_FRIEND
        if responses:
            ContextData.last_messages.append(message)
            ContextData.current_responses = responses
            try:
                await ResponseMethods.send_response(client, message, responses)
            except FloodWait as e:
                await asyncio.sleep(e.value)


class ResponseUpdater:
    @staticmethod
    async def update_response(client: Client):
        if ContextData.last_messages and ContextData.current_responses:
            message = random.choice(ContextData.last_messages)
            try:
                await ResponseMethods.send_response(client,
                                                    message,
                                                    ContextData.current_responses)
            except FloodWait as e:
                await asyncio.sleep(e.value)


async def main():
    async with app:
        await ContextData.check_premium(app)
        app.add_handler(MessageHandler(ResponseHandler.message_handler))
        scheduler = AsyncIOScheduler()
        trigger = IntervalTrigger(seconds=const.UPDATE_TIMEOUT, jitter=const.UPDATE_JITTER)
        scheduler.add_job(ResponseUpdater.update_response, trigger, args=[app, ])
        scheduler.start()
        await idle()


app.run(main())
