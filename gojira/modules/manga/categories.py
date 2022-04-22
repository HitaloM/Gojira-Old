# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import anilist
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_callback_query(filters.regex(r"^categories manga (?P<page>\d+)"))
@use_chat_language()
async def manga_categories(bot: Gojira, callback: CallbackQuery):
    page = int(callback.matches[0]["page"])

    message = callback.message
    lang = callback._lang

    # fmt: off
    categories = [
        "action", "shounen",
        "martial_arts", "adventure",
        "comedy", "ecchi",
        "devils", "drama",
        "fantasy", "yuri",
        "yaoi", "school",
        "sports", "space",
        "hentai", "isekai",
        "shoujo", "fight",
        "mystery", "supernatural",
        "music", "slice_of_life",
    ]
    categories.sort()
    # fmt: on

    layout = Pagination(
        categories,
        item_data=lambda i, pg: f"categorie manga {i} 1",
        item_title=lambda i, pg: lang.strings[lang.code][i],
        page_data=lambda pg: f"categories manga {pg}",
    )

    lines = layout.create(page, lines=8, columns=2)

    keyboard = []
    if len(lines) > 0:
        keyboard += lines

    keyboard.append([(lang.back_button, "manga")])

    await message.edit_text(
        lang.categories_text,
        reply_markup=ikb(keyboard),
    )


@Gojira.on_callback_query(
    filters.regex(r"^categorie manga (?P<categorie>\w+) (?P<page>\d+)")
)
@use_chat_language()
async def manga_categorie(bot: Gojira, callback: CallbackQuery):
    categorie = callback.matches[0]["categorie"]
    page = int(callback.matches[0]["page"])

    message = callback.message
    lang = callback._lang

    genre = categorie.replace("_", " ")
    results = await anilist.AsyncClient().search(genre, "manga", 50)

    layout = Pagination(
        results,
        item_data=lambda i, pg: f"manga {i.id}",
        item_title=lambda i, pg: i.title.romaji,
        page_data=lambda pg: f"categorie manga {categorie} {pg}",
    )

    lines = layout.create(page, lines=8)

    keyboard = []
    if len(lines) > 0:
        keyboard += lines

    keyboard.append([(lang.back_button, "categories manga 1")])

    await message.edit_text(
        lang.categorie_text.format(genre=lang.strings[lang.code][categorie]),
        reply_markup=ikb(keyboard),
    )
