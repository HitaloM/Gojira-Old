# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from typing import Union

from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"about$"))
@Gojira.on_callback_query(filters.regex(r"^about$"))
@use_chat_language()
async def about(bot: Gojira, union: Union[CallbackQuery, Message]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    lang = union._lang

    keyboard = [
        [
            (lang.github_button, "https://github.com/HitaloSama/Gojira", "url"),
            (lang.channel_button, "https://t.me/HitaloProjects", "url"),
        ]
    ]

    is_private = await filters.private(bot, message)
    if is_private:
        keyboard.append(
            [
                (lang.back_button, "start"),
            ],
        )

    await (message.edit_text if is_callback else message.reply_text)(
        lang.about_text.format(
            bot_name=bot.me.first_name,
            version=f"<a href='https://github.com/HitaloSama/Gojira/commit/{bot.version}'>{bot.version}</a>",
            version_code=bot.version_code,
        ),
        disable_web_page_preview=True,
        reply_markup=ikb(keyboard),
    )
