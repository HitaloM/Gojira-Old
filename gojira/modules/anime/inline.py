# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
import re
from typing import List

import anilist
from pyrogram import filters
from pyrogram.errors import QueryIdInvalid
from pyrogram.helpers import ikb
from pyrogram.types import InlineQuery, InlineQueryResultPhoto

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_inline_query(filters.regex(r"^(?P<query>.+)"))
@use_chat_language()
async def anime_inline(bot: Gojira, inline_query: InlineQuery):
    query = inline_query.matches[0]["query"].strip()
    lang = inline_query._lang

    if query.startswith("!"):
        inline_query.continue_propagation()

    results: List[InlineQueryResultPhoto] = []

    async with anilist.AsyncClient() as client:
        search_results = await client.search(query, "anime", page=1, limit=15)
        while search_results is None:
            await asyncio.sleep(0.5)
            search_results = await client.search(query, "anime", page=1, limit=10)

        for result in search_results:
            anime = await client.get(result.id, "anime")

            if anime is None:
                continue

            photo: str = ""
            if hasattr(anime, "banner"):
                photo = anime.banner
            elif hasattr(anime, "cover"):
                if hasattr(anime.cover, "extra_large"):
                    photo = anime.cover.extra_large
                elif hasattr(anime.cover, "large"):
                    photo = anime.cover.large
                elif hasattr(anime.cover, "medium"):
                    photo = anime.cover.medium

            description: str = ""
            if hasattr(anime, "description"):
                description = anime.description
                description = re.sub(re.compile(r"<.*?>"), "", description)
                description = description[0:260] + "..."

            text = f"<b>{anime.title.romaji}</b>"
            if hasattr(anime.title, "native"):
                text += f" (<code>{anime.title.native}</code>)"
            text += f"\n\n<b>ID</b>: <code>{anime.id}</code> (<b>ANIME</b>)"
            if hasattr(anime, "score") and hasattr(anime.score, "average"):
                text += f"\n<b>{lang.score}</b>: <code>{anime.score.average}</code>"
            text += f"\n<b>{lang.status}</b>: <code>{anime.status}</code>"
            if hasattr(anime, "genres"):
                text += (
                    f"\n<b>{lang.genres}</b>: <code>{', '.join(anime.genres)}</code>"
                )
            if hasattr(anime, "studios"):
                text += (
                    f"\n<b>{lang.studios}</b>: <code>{', '.join(anime.studios)}</code>"
                )
            if hasattr(anime, "format"):
                text += f"\n<b>{lang.format}</b>: <code>{anime.format}</code>"
            if not anime.status.lower() == "not_yet_released":
                text += f"\n<b>{lang.start_date}</b>: <code>{anime.start_date.day if hasattr(anime.start_date, 'day') else 0}/{anime.start_date.month if hasattr(anime.start_date, 'month') else 0}/{anime.start_date.year if hasattr(anime.start_date, 'year') else 0}</code>"
            if not anime.status.lower() in ["not_yet_released", "releasing"]:
                text += f"\n<b>{lang.end_date}</b>: <code>{anime.end_date.day if hasattr(anime.end_date, 'day') else 0}/{anime.end_date.month if hasattr(anime.end_date, 'month') else 0}/{anime.end_date.year if hasattr(anime.end_date, 'year') else 0}</code>"

            text += f"\n\n<b>{lang.short_description}</b>: <i>{description}</i>"

            keyboard = [
                [
                    (
                        lang.view_more_button,
                        f"https://t.me/{bot.me.username}/?start=anime_{anime.id}",
                        "url",
                    )
                ],
            ]

            if hasattr(anime, "format"):
                anime_format = "| " + anime.format
            else:
                anime_format = None

            results.append(
                InlineQueryResultPhoto(
                    photo_url=photo,
                    title=f"{anime.title.romaji} {anime_format}",
                    description=description,
                    caption=text,
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
