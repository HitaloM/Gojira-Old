# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from gojira.database.chats import get_chat_by_id
from gojira.database.users import get_user_by_id
from gojira.utils.langs import chat_languages, user_languages


async def get_user_lang(user_id: int) -> str:
    if user_id not in user_languages:
        user = await get_user_by_id(user_id)
        userlang = user_languages[user_id] = "en" if user is None else user["language"]
    else:
        userlang = None
    return userlang


async def get_chat_lang(chat_id: int) -> str:
    if chat_id not in chat_languages:
        chat = await get_chat_by_id(chat_id)
        chatlang = chat_languages[chat_id] = "en" if chat is None else chat["language"]
    else:
        chatlang = None
    return chatlang
