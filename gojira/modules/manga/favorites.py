# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>
# SOFTWARE.

import anilist
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from gojira.bot import Gojira
from gojira.database.favorites import filter_user_favorites
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_callback_query(filters.regex(r"favorites manga (?P<page>\d+)"))
@use_chat_language()
async def manga_favorites(bot: Gojira, callback: CallbackQuery):
    page = int(callback.matches[0]["page"])

    message = callback.message
    user = callback.from_user
    lang = callback._lang

    keyboard = []
    async with anilist.AsyncClient() as client:
        favorites = await filter_user_favorites(user=user.id, type="manga")

        results = []
        for favorite in favorites:
            manga = await client.get(favorite["item"], "manga")
            results.append((favorite, manga))

        layout = Pagination(
            results,
            item_data=lambda i, pg: f"manga {i[0]['item']}",
            item_title=lambda i, pg: i[1].title.romaji,
            page_data=lambda pg: f"favorites manga {pg}",
        )

        lines = layout.create(page, lines=8)

        if len(lines) > 0:
            keyboard += lines

    keyboard.append([(lang.back_button, "manga")])

    await message.edit_text(
        lang.favorites_text,
        reply_markup=ikb(keyboard),
    )
