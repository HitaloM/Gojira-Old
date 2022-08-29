# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import httpx
from anilist.types import Anime
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_callback_query(filters.regex(r"^upcoming anime (?P<page>\d+)"))
@use_chat_language()
async def anime_upcoming(bot: Gojira, callback: CallbackQuery):
    page = int(callback.matches[0]["page"])

    message = callback.message
    lang = callback._lang

    keyboard = []
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(
            url="https://graphql.anilist.co",
            json=dict(
                query="""
                query($per_page: Int) {
                    Page(page: 1, perPage: $per_page) {
                        media(type: ANIME, sort: POPULARITY_DESC, status: NOT_YET_RELEASED) {
                            id
                            title {
                                romaji
                                english
                                native
                            }
                            siteUrl
                        }
                    }
                }
                """,
                variables=dict(
                    per_page=50,
                ),
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        data = response.json()
        await client.aclose()
        if data["data"]:
            items = data["data"]["Page"]["media"]
            suggestions = [
                Anime(id=item["id"], title=item["title"], url=item["siteUrl"])
                for item in items
            ]

            layout = Pagination(
                suggestions,
                item_data=lambda i, pg: f"anime {i.id}",
                item_title=lambda i, pg: i.title.romaji,
                page_data=lambda pg: f"upcoming anime {pg}",
            )

            lines = layout.create(page, lines=8)

            if len(lines) > 0:
                keyboard += lines

    keyboard.append([(lang.back_button, "anime")])

    await message.edit_text(
        lang.upcoming_text,
        reply_markup=ikb(keyboard),
    )
