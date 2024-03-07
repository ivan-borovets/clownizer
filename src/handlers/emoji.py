import random
from pyrogram import Client
from pyrogram.errors import FloodWait, ReactionInvalid, MessageNotModified
from pyrogram.raw import functions
from pyrogram.raw.types import ReactionEmoji
from pyrogram.types import Message, MessageReactions
from typing import Optional

import settings
from context import Context
from console_logger import ConsoleLogger
from handlers.flood import FloodHandler
from settings import logger


class EmojiHandler:
    @staticmethod
    def get_target_friendship_status(
        message: Message,
    ) -> Optional[settings.FriendshipStatus]:
        """
        For a given message, returns the friendship status of its author
        """
        target = settings.TARGETS.get(message.from_user.id)
        if target:
            return target[1]

    @classmethod
    def from_friendship_to_emojis(
        cls, message: Message
    ) -> Optional[list[ReactionEmoji]]:
        """
        Returns a list of ReactionEmojis if the message's author is in the list of targets
        """
        target_friendship_status = cls.get_target_friendship_status(message)
        if target_friendship_status is not None:
            suitable_emoticons: tuple = settings.EMOTICONS_BY_FRIENDSHIP[
                target_friendship_status == settings.FriendshipStatus.ENEMY
            ]
            picked_emoticons: list[str] = Context.emoticon_picker(suitable_emoticons)
            emojis: list[ReactionEmoji] = cls.convert(picked_emoticons)
            return emojis

    @staticmethod
    async def place(
        client: Client, message: Message, emojis: list[ReactionEmoji]
    ) -> int:
        """
        Places ReactionEmojis on message if possible,
        Returns error codes for further log processing
        """
        try:
            await client.invoke(
                functions.messages.SendReaction(
                    peer=await client.resolve_peer(message.chat.id),
                    msg_id=message.id,
                    add_to_recent=True,
                    reaction=emojis,
                )
            )
            return 0
        except ReactionInvalid:
            emoticons: list[str] = [x.emoticon for x in emojis]
            logger.error(
                f"Reactions {', '.join(emoticons)} were not sent!\n"
                f"Some of these reactions are invalid in this chat.\n"
                f"You can try to correct the Settings file."
            )
            return 1
        except MessageNotModified:
            logger.error("Message was not modified due to Telegram peculiarities")
            return 1

    @staticmethod
    def convert(emoticons: list[str]) -> list[ReactionEmoji]:
        """
        Converts emoticons of type string into ReactionEmojis
        """
        return [ReactionEmoji(emoticon=e) for e in emoticons]

    @classmethod
    async def respond(cls, client: Client, message: Message) -> None:
        """
        Replies to a message of a target with ReactionEmojis
        """
        if message is not None and message.from_user:
            emojis = cls.from_friendship_to_emojis(message)
            if emojis is not None:
                try:
                    error_code = await cls.place(
                        client=client, message=message, emojis=emojis
                    )
                    if not error_code:
                        Context.last_messages.append(message)
                        await ConsoleLogger.log(
                            fun_name=cls.respond.__name__.title(),
                            message=message,
                            emojis=emojis,
                        )
                except FloodWait as f:
                    await FloodHandler.handle(f)

    @classmethod
    async def update(cls, client: Client) -> None:
        """
        Updates the previously placed ReactionEmojis
        """
        if Context.last_messages:
            random_message: Message = random.choice(Context.last_messages)
            current_message: Message = await client.get_messages(
                random_message.from_user.id, random_message.id
            )
            if current_message.reactions:
                cur_msg_reacts: MessageReactions = (
                    current_message.reactions
                )  # Wrong type annotation, not my fault
                current_emojis_set = {obj.emoji for obj in cur_msg_reacts.reactions}
                while True:
                    new_emojis = cls.from_friendship_to_emojis(current_message)
                    if new_emojis is not None:
                        new_emojis_set = {obj.emoticon for obj in new_emojis}
                        if current_emojis_set == new_emojis_set:
                            logger.info(
                                "The generated emojis are the same as previously placed.\n"
                                "Trying to generate a different set of emojis."
                            )
                        else:
                            try:
                                error_code = await cls.place(
                                    client=client,
                                    message=current_message,
                                    emojis=new_emojis,
                                )
                                if not error_code:
                                    await ConsoleLogger.log(
                                        fun_name=cls.update.__name__.title(),
                                        message=current_message,
                                        emojis=new_emojis,
                                    )
                            except FloodWait as f:
                                await FloodHandler.handle(f)
                            break
