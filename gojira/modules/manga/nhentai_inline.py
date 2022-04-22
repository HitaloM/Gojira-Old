# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
import re
from typing import List

import bs4
import httpx
import telegraph
from pyrogram import filters
from pyrogram.errors import QueryIdInvalid
from pyrogram.helpers import ikb
from pyrogram.types import InlineQuery, InlineQueryResultPhoto

from gojira.bot import Gojira
from gojira.database import nHentai
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_inline_query(filters.regex(r"^!nh (?P<query>.+)"))
@use_chat_language()
async def nhentai_inline(bot: Gojira, inline_query: InlineQuery):
    query = inline_query.matches[0]["query"].strip()
    lang = inline_query._lang

    results: List[InlineQueryResultPhoto] = []

    if query.isdecimal():
        search_results = [await get_data(int(query))]
    else:
        search_results = [
            *filter(
                lambda manga: query.lower() in manga.title.lower(), await nHentai.all()
            )
        ]

    for manga in search_results:
        if manga is None:
            continue

        if len(results) >= 15:
            break

        text = f"<b>{manga.title}</b>"
        text += f"\n\n<b>ID</b>: <code>{manga.id}</code> (<b>NHENTAI</b>)"
        text += f"\n<b>{lang.artist}</b>: <a href=\"https://nhentai.net/artist/{manga.artist.replace(' ', '-')}/\">{manga.artist}</a>"
        tags = [
            f"<a href=\"https://nhentai.net/tag/{tag.replace(' ', '-')}/\">{tag}</a>"
            for tag in manga.tags.split(", ")
        ]
        text += f"\n<b>{lang.tags}</b>: {', '.join(tags)}"
        text += f"\n<b>{lang.page}s</b>: <code>{manga.pages}</code>"

        results.append(
            InlineQueryResultPhoto(
                photo_url=manga.photo,
                title=manga.title,
                description=manga.tags,
                caption=text,
                reply_markup=ikb(
                    [
                        [
                            (
                                "👠 nHentai",
                                f"https://nhentai.net/g/{manga.id}",
                                "url",
                            ),
                            (lang.read_button, manga.url, "url"),
                        ]
                    ]
                ),
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


async def get_data(m_id: int):
    nhentai = await nHentai.get_or_none(id=m_id)

    if nhentai is None:
        artist, photo, title, pages, url = (None,) * 5

        async with httpx.AsyncClient(http2=True) as client:
            response = await client.get(f"https://nhentai.net/g/{m_id}")

            if response.status_code == 200:
                soup = bs4.BeautifulSoup(response.text, "html.parser")

                cover = soup.find("div", id="cover")
                photo = cover.a.img["data-src"]

                content = soup.find("div", id="content")

                h1 = content.find("h1", "title")
                title = ""
                for span in h1.find_all("span"):
                    if span.string is not None:
                        title += span.string

                tags = []
                section = content.find("section", id="tags")
                for span in section.find_all("span", **{"class": "name"}):
                    tags.append(span.string)
                tags = ", ".join(tags)

                artist = section.find("a", href=re.compile("artist")).span.string
                pages = int(section.find("a", href=re.compile("q=pages")).span.string)
            else:
                return None

            await client.aclose()

        tgph = telegraph.Telegraph()
        tgph.create_account(
            short_name="PyGodzillaBot",
            author_name="@PyGodzillaBot",
            author_url="https://t.me/PyGodzillaBot",
        )

        html_content = ""
        async with httpx.AsyncClient(http2=True) as client:
            response = await client.get(f"https://cin.cin.pw/v/{m_id}")
            while not response.status_code == 200:
                response = await client.get(f"https://cin.cin.pw/v/{m_id}")
                await asyncio.sleep(0.5)

            soup = bs4.BeautifulSoup(response.text, "html.parser")
            for img in soup.find_all("img", **{"class": "hentai-page"}):
                html_content += f"<img src=\"{img['src']}\"/>\n"

            await client.aclose()

        page = tgph.create_page(
            title=title,
            html_content=html_content,
            author_name="@PyGodzillaBot",
            author_url="https://t.me/PyGodzillaBot",
        )
        url = page["url"]

        nhentai = await nHentai.create(
            id=m_id,
            artist=artist,
            photo=photo,
            title=title,
            pages=pages,
            tags=tags,
            url=url,
        )

    return nhentai
