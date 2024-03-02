import asyncio
import os
import random
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.raw.types import ReactionEmoji
from collections import deque

from dotenv import load_dotenv
import const

load_dotenv()
app = Client(name="my_account",
             api_id=os.getenv('api_id'),
             api_hash=os.getenv('api_hash'), )


class ContextData:
    is_premium = None
    response_method = None
    current_responses = None
    last_messages = deque(maxlen=const.MESSAGE_MEMORY_SIZE)

    @staticmethod
    def choice_method(responses):
        return random.choice(responses)

    @staticmethod
    def sample_method(responses):
        return random.sample(responses, k=min(3, len(responses)))

    @classmethod
    async def check_premium(cls, client):
        user = await client.get_me()
        cls.is_premium = user.is_premium

    @classmethod
    def set_response_method(cls):
        cls.response_method = (cls.choice_method, cls.sample_method)[cls.is_premium]

    @classmethod
    async def send_response(cls, message, responses):
        cls.set_response_method()
        random_responses = cls.response_method(responses)
        await app.invoke(
            functions.messages.SendReaction(
                peer=await app.resolve_peer(message.chat.id),
                msg_id=message.id,
                add_to_recent=True,
                reaction=[ReactionEmoji(emoticon=response) for response in random_responses]
            )
        )

    @classmethod
    async def refresh_response(cls):
        while True:
            if cls.last_messages and cls.current_responses:
                message = random.choice(cls.last_messages)
                await cls.send_response(message, cls.current_responses)
            sleep_time = random.randint(*const.REFRESH_SLEEP_TIME)
            try:
                await asyncio.sleep(sleep_time)
            except FloodWait as e:
                await asyncio.sleep(e.value)


async def message_handler(client, message: Message):
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
            await ContextData.send_response(message, responses)
        except FloodWait as e:
            await asyncio.sleep(e.value)


async def main():
    async with app:
        await ContextData.check_premium(client=app)
        app.add_handler(MessageHandler(message_handler))
        asyncio.ensure_future(ContextData.refresh_response())
        await idle()


app.run(main())
