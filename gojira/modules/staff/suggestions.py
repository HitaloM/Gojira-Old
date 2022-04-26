# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>

import httpx
from anilist.types import Character
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_callback_query(filters.regex(r"^popular staff (?P<page>\d+)"))
@use_chat_language()
async def staff_popular(bot: Gojira, callback: CallbackQuery):
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
                        staff(sort: FAVOURITES_DESC) {
                            id
                            name {
                                first
                                full
                                native
                                last
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
            items = data["data"]["Page"]["staff"]
            suggestions = [
                Character(id=item["id"], name=item["name"], url=item["siteUrl"])
                for item in items
            ]

            layout = Pagination(
                suggestions,
                item_data=lambda i, pg: f"staff {i.id}",
                item_title=lambda i, pg: i.name.full,
                page_data=lambda pg: f"popular staff {pg}",
            )

            lines = layout.create(page, lines=8)

            if len(lines) > 0:
                keyboard += lines

    keyboard.append([(lang.back_button, "staff")])

    await message.edit_text(
        lang.favourites_text,
        reply_markup=ikb(keyboard),
    )
