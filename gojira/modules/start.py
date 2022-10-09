# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import re
from typing import Union

from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.modules.anime.view import anime_view
from gojira.modules.character.view import character_view
from gojira.modules.manga.view import manga_view
from gojira.modules.staff.view import staff_view
from gojira.modules.studio.view import studio_view
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"start$"))
@Gojira.on_callback_query(filters.regex(r"^start$"))
@use_chat_language()
async def start(bot: Gojira, union: Union[CallbackQuery, Message]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    lang = union._lang

    if await filters.private(bot, message):
        await (message.edit_text if is_callback else message.reply_text)(
            lang.start_text.format(
                user_mention=user.mention(),
                bot_name=bot.me.first_name,
            ),
            reply_markup=ikb(
                [
                    [
                        (lang.about_button, "about"),
                        (lang.language_button, "language"),
                    ],
                    [
                        (lang.help_button, "help"),
                    ],
                ]
            ),
        )
    else:
        await message.reply_text(
            lang.start_text_2.format(
                user_mention=user.mention(),
                bot_name=bot.me.first_name,
            ),
        )


@Gojira.on_message(filters.cmd(r"help$"))
@Gojira.on_message(filters.cmd(r"start help$") & filters.private)
@Gojira.on_callback_query(filters.regex(r"^help$"))
@use_chat_language()
async def help(bot: Gojira, union: Union[Message, CallbackQuery]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    lang = union._lang

    if await filters.private(bot, message):
        await (message.edit_text if is_callback else message.reply_text)(
            lang.help_text,
            reply_markup=ikb(
                [
                    [
                        (lang.anime_button, "anime"),
                        (lang.manga_button, "manga"),
                        (lang.character_button, "character"),
                    ],
                    [
                        (lang.staff_button, "staff"),
                        (lang.studio_button, "studio"),
                    ],
                    [
                        (lang.back_button, "start"),
                    ],
                ]
            ),
        )
    else:
        await message.reply_text(
            lang.help_text_2.format(
                user_mention=user.mention(),
                bot_name=bot.me.first_name,
            ),
            reply_markup=ikb(
                [
                    [
                        (
                            lang.start_button,
                            f"https://t.me/{bot.me.username}?start=help",
                            "url",
                        )
                    ]
                ]
            ),
        )


@Gojira.on_message(
    filters.cmd(r"start (?P<content_type>anime|character|staff|studio|manga)_(\d+)")
    & filters.private
)
async def view(bot: Gojira, message: Message):
    content_type = message.matches[0]["content_type"]

    matches = re.search(r"(\d+)", message.text)
    message.matches = [matches]

    if content_type == "anime":
        await anime_view(bot, message)
    elif content_type == "character":
        await character_view(bot, message)
    elif content_type == "staff":
        await staff_view(bot, message)
    elif content_type == "studio":
        await studio_view(bot, message)
    else:
        await manga_view(bot, message)
