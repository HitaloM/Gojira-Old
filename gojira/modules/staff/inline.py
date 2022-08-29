# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
import re
from typing import List

import anilist
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import QueryIdInvalid
from pyrogram.helpers import ikb
from pyrogram.types import InlineQuery, InlineQueryResultPhoto

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_inline_query(filters.regex(r"^!s (?P<query>.+)"))
@use_chat_language()
async def staff_inline(bot: Gojira, inline_query: InlineQuery):
    query = inline_query.matches[0]["query"].strip()
    lang = inline_query._lang

    results: List[InlineQueryResultPhoto] = []

    async with anilist.AsyncClient() as client:
        search_results = await client.search(query, "staff", page=1, limit=15)
        while search_results is None:
            await asyncio.sleep(0.5)
            search_results = await client.search(query, "staff", page=1, limit=10)

        for result in search_results:
            staff = await client.get(result.id, "staff")

            if staff is None:
                continue

            photo: str = ""
            if hasattr(staff, "image"):
                if hasattr(staff.image, "large"):
                    photo = staff.image.large
                elif hasattr(staff.image, "medium"):
                    photo = staff.image.medium

            description: str = ""
            if hasattr(staff, "description"):
                description = staff.description
                description = description.replace("__", "")
                description = description.replace("**", "")
                description = description.replace("~", "")
                description = re.sub(re.compile(r"<.*?>"), "", description)
                description = description[0:260] + "..."

            text = f"<b>{staff.name.full}</b>"
            text += f"\n<b>ID</b>: <code>{staff.id}</code> (<b>STAFF</b>)"
            if hasattr(staff, "favorites"):
                text += f"\n<b>{lang.favorite}s</b>: <code>{staff.favorites}</code>"

            text += f"\n\n{description}"

            keyboard = [
                [
                    (
                        lang.view_more_button,
                        f"https://t.me/{bot.me.username}/?start=staff_{staff.id}",
                        "url",
                    )
                ],
            ]

            results.append(
                InlineQueryResultPhoto(
                    photo_url=photo,
                    title=staff.name.full,
                    description=description,
                    caption=text,
                    parse_mode=ParseMode.DEFAULT,
                    reply_markup=ikb(keyboard),
                )
            )

    if len(results) > 0:
        try:
            await inline_query.answer(
                results=results,
                is_gallery=False,
                cache_time=3,
            )
        except QueryIdInvalid:
            pass
