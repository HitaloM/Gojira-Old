# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import re

from pyrogram import filters
from pyrogram.types import Message

from gojira.bot import Gojira
from gojira.modules.anime.view import anime_view
from gojira.modules.character.view import character_view
from gojira.modules.manga.view import manga_view
from gojira.modules.staff.view import staff_view


@Gojira.on_message(filters.private & filters.via_bot)
async def view(bot: Gojira, message: Message):
    from_bot = message.via_bot

    if from_bot.id == bot.me.id and bool(message.photo) and bool(message.caption):
        text = message.caption
        lines = text.splitlines()

        for line in lines:
            if "ID" in line:
                matches = re.match(r"ID: (\d+) \((\w+)\)", line)
                content_type = matches.group(2).lower()
                message.matches = [matches]
                if content_type == "anime":
                    await anime_view(bot, message)
                elif content_type == "character":
                    await character_view(bot, message)
                elif content_type == "staff":
                    await staff_view(bot, message)
                elif content_type == "manga":
                    await manga_view(bot, message)
