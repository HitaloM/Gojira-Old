# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from pyrogram.enums import ChatType
from pyrogram.types import CallbackQuery, InlineQuery, Message

from gojira.bot import Gojira
from gojira.database.chats import get_chat_by_id, register_chat_by_dict
from gojira.database.users import get_user_by_id, register_user_by_dict


@Gojira.on_message(group=-1)
async def check_chat(bot: Gojira, message: Message):
    chat = message.chat
    user = message.from_user
    if not user:
        return

    if chat.type == ChatType.PRIVATE and await get_user_by_id(user.id) is None:
        await register_user_by_dict(user.__dict__)
    if (
        chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
        and await get_chat_by_id(chat.id) is None
    ):
        await register_chat_by_dict(chat.__dict__)


@Gojira.on_callback_query(group=-1)
async def set_language_callback(bot: Gojira, callback: CallbackQuery):
    chat = callback.message.chat
    user = callback.from_user
    if not user:
        return

    if chat.type == ChatType.PRIVATE and await get_user_by_id(user.id) is None:
        await register_user_by_dict(user.__dict__)
    if (
        chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
        and await get_chat_by_id(chat.id) is None
    ):
        await register_chat_by_dict(chat.__dict__)


@Gojira.on_inline_query(group=-1)
async def set_language_inline_query(bot: Gojira, inline_query: InlineQuery):
    user = inline_query.from_user
    if not user:
        return

    if await get_user_by_id(user.id) is None:
        await register_user_by_dict(user.__dict__)


@Gojira.on_edited_message(group=-1)
async def edited(bot: Gojira, message: Message):
    message.stop_propagation()
