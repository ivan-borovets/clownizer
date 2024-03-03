import asyncio
import os
import random
import uvloop
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
uvloop.install()
app = Client(name="my_account",
             api_id=os.getenv('API_ID'),
             api_hash=os.getenv('API_HASH'), )


class ContextData:
    class ResponsePickMethods:
        @staticmethod
        def choice(responses):
            return random.choice(responses)

        @staticmethod
        def sample(responses):
            return random.sample(responses, k=min(3, len(responses)))

    is_premium = None
    response_picker = None
    last_messages = deque(maxlen=const.MESSAGE_MEMORY_SIZE)

    @classmethod
    async def set_premium(cls, client: Client):
        user = await client.get_me()
        cls.is_premium = user.is_premium

    @classmethod
    async def set_response_picker(cls, client: Client):
        if cls.is_premium is None:
            await cls.set_premium(client)
        cls.response_picker = (cls.ResponsePickMethods.choice, cls.ResponsePickMethods.sample)[cls.is_premium]


class ResponseGenerator:
    @staticmethod
    def filter(message: Message):
        responses = ()
        if message is not None and message.from_user:
            target = const.TARGETS.get(message.from_user.id, ())
            if target:
                _, status = target
                if status in const.UserStatus:
                    responses = (const.RESPONSE_TO_FRIEND, const.RESPONSE_TO_ENEMY)[status == const.UserStatus.ENEMY]
        return responses

    @classmethod
    def generate(cls, message: Message):
        filtered_responses = cls.filter(message)
        picked_responses = ContextData.response_picker(filtered_responses)
        return picked_responses


class ReactionsGenerator:
    @staticmethod
    def generate(responses):
        return [ReactionEmoji(emoticon=response) for response in responses]


class ReactionsCompositor:
    @staticmethod
    def compose(message: Message):
        generated_responses = ResponseGenerator.generate(message)
        generated_reactions = ReactionsGenerator.generate(generated_responses)
        return generated_reactions


class ReactionsPlacer:
    @staticmethod
    async def invoke(client: Client, message: Message, reactions):
        await client.invoke(
            functions.messages.SendReaction(
                peer=await client.resolve_peer(message.chat.id),
                msg_id=message.id,
                add_to_recent=True,
                reaction=reactions
            )
        )

    @classmethod
    async def send(cls, client: Client, message: Message):
        generated_reactions = ReactionsCompositor.compose(message)
        if generated_reactions:
            ContextData.last_messages.append(message)
            try:
                await cls.invoke(client, message, generated_reactions)
            except FloodWait as e:
                await asyncio.sleep(e.value)

    @classmethod
    async def update(cls, client: Client):
        if ContextData.last_messages:
            random_message: Message = random.choice(ContextData.last_messages)
            current_message = await client.get_messages(random_message.from_user.id, random_message.id)
            if current_message.reactions:
                while True:
                    generated_reactions = ReactionsCompositor.compose(current_message)
                    generated_reactions_set = {obj.emoticon for obj in generated_reactions}
                    current_reactions_set = {obj.emoji for obj in current_message.reactions.reactions}
                    if generated_reactions_set != current_reactions_set:
                        try:
                            await cls.invoke(client, current_message, generated_reactions)
                            break
                        except FloodWait as e:
                            await asyncio.sleep(e.value)


class ConstValidator:
    @staticmethod
    def validate():
        is_correct_user_status = {item.name for item in const.UserStatus} == {'FRIEND', 'ENEMY'}
        is_enough_responses = (len(const.RESPONSE_TO_FRIEND) > (1, 3)[ContextData.is_premium] and
                               len(const.RESPONSE_TO_ENEMY) > (1, 3)[ContextData.is_premium])
        is_enough_targets = len(const.TARGETS) > 0
        is_enough_memory = const.MESSAGE_MEMORY_SIZE > 0
        return all((is_correct_user_status,
                    is_enough_responses,
                    is_enough_targets,
                    is_enough_memory))


class ConstantsException(Exception):
    pass


async def main():
    async with app:
        await ContextData.set_response_picker(app)
        if ConstValidator.validate():
            print("The constants look fine, the program works...")
        else:
            raise ConstantsException("The program launch failed. Check the constants in const.py!")
        app.add_handler(MessageHandler(ReactionsPlacer.send))
        scheduler = AsyncIOScheduler()
        trigger = IntervalTrigger(seconds=const.UPDATE_TIMEOUT, jitter=const.UPDATE_JITTER)
        scheduler.add_job(ReactionsPlacer.update, trigger, args=[app, ], id='1', replace_existing=True)
        scheduler.start()
        await idle()


app.run(main())
