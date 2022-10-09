# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>

# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>

from typing import Union

from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"studio$") & filters.private)
@Gojira.on_callback_query(filters.regex(r"^studio$"))
@use_chat_language()
async def studio_start(bot: Gojira, union: Union[CallbackQuery, Message]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    lang = union._lang

    keyboard = [
        [
            (lang.char_favs_button, "popular studio 1"),
            (lang.favorites_button, "favorites studio 1"),
        ],
    ]

    if is_callback:
        keyboard.append([(lang.back_button, "help")])

    await (message.edit_text if is_callback else message.reply_text)(
        lang.studio_text,
        reply_markup=ikb(keyboard),
    )
