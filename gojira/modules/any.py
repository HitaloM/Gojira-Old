# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineQuery, Message

from gojira.bot import Gojira
from gojira.database.chats import get_chat_by_id, register_chat_by_dict
from gojira.database.users import get_user_by_id, register_user_by_dict


@Gojira.on_message(group=-1)
async def check_chat(c: Gojira, m: Message):
    if m.chat.type == "private" and await get_user_by_id(m.from_user.id) is None:
        await register_user_by_dict(m.from_user.__dict__)
    if (
        m.chat.type in ["group", "supergroup"]
        and await get_chat_by_id(m.chat.id) is None
    ):
        await register_chat_by_dict(m.chat.__dict__)


@Gojira.on_callback_query(group=-1)
async def set_language_callback(c: Gojira, callback: CallbackQuery):
    chat = callback.message.chat
    user = callback.from_user
    if not user:
        return

    if chat.type == "private" and await get_user_by_id(user.id) is None:
        await register_user_by_dict(user.__dict__)
    if chat.type in ["group", "supergroup"] and await get_chat_by_id(chat.id) is None:
        await register_chat_by_dict(chat.__dict__)


@Gojira.on_inline_query(group=-1)
async def set_language_inline_query(c: Gojira, inline_query: InlineQuery):
    user = inline_query.from_user
    if not user:
        return

    if await get_user_by_id(user.id) is None:
        await register_user_by_dict(user.__dict__)


@Gojira.on_message(filters.edited)
async def edited(c: Gojira, m: Message):
    m.stop_propagation()
