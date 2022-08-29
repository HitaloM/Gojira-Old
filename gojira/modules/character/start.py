# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>

from typing import Union

from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"character$") & filters.private)
@Gojira.on_callback_query(filters.regex(r"^character$"))
@use_chat_language()
async def character_start(bot: Gojira, union: Union[CallbackQuery, Message]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    lang = union._lang

    keyboard = [
        [
            (lang.char_favs_button, "popular character 1"),
            (lang.favorites_button, "favorites character 1"),
        ],
        [
            (lang.search_button, "!c ", "switch_inline_query_current_chat"),
        ],
    ]

    if is_callback:
        keyboard.append([(lang.back_button, "help")])

    await (message.edit_text if is_callback else message.reply_text)(
        lang.character_text,
        reply_markup=ikb(keyboard),
    )
