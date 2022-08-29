# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>

import anilist
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from gojira.bot import Gojira
from gojira.database.favorites import filter_user_favorites
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_callback_query(filters.regex(r"favorites staff (?P<page>\d+)"))
@use_chat_language()
async def character_favorites(bot: Gojira, callback: CallbackQuery):
    page = int(callback.matches[0]["page"])

    message = callback.message
    user = callback.from_user
    lang = callback._lang

    keyboard = []
    async with anilist.AsyncClient() as client:
        favorites = await filter_user_favorites(user=user.id, type="staff")

        results = []
        for favorite in favorites:
            staff = await client.get(favorite["item"], "staff")
            results.append((favorite, staff))

        layout = Pagination(
            results,
            item_data=lambda i, pg: f"staff {i[0]['item']}",
            item_title=lambda i, pg: i[1].name.full,
            page_data=lambda pg: f"favorites staff {pg}",
        )

        lines = layout.create(page, lines=8)

        if len(lines) > 0:
            keyboard += lines

    keyboard.append([(lang.back_button, "staff")])

    await message.edit_text(
        lang.favorites_text,
        reply_markup=ikb(keyboard),
    )
