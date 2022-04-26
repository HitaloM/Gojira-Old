# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
from typing import List

import httpx
from pyrogram import filters
from pyrogram.errors import QueryIdInvalid
from pyrogram.helpers import ikb
from pyrogram.types import InlineQuery, InlineQueryResultPhoto
from telegraph.aio import Telegraph

from gojira.bot import Gojira
from gojira.database.nhentai import create_nhentai, get_nhentai_all, get_nhentai_by_id
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
                lambda manga: query.lower() in manga["title"].lower(),
                await get_nhentai_all(),
            )
        ]

    for manga in search_results:
        if manga is None:
            continue

        if len(results) >= 15:
            break

        text = f"<b>{manga['title']}</b>"
        text += f"\n\n<b>ID</b>: <code>{manga['id']}</code> (<b>NHENTAI</b>)"
        text += f"\n<b>{lang.artist}</b>: <a href=\"https://nhentai.net/artist/{manga['artist'].replace(' ', '-')}/\">{manga['artist']}</a>"
        tags = [
            f"<a href=\"https://nhentai.net/tag/{tag.replace(' ', '-')}/\">{tag}</a>"
            for tag in manga["tags"].split(", ")
        ]
        text += f"\n<b>{lang.tags}</b>: {', '.join(tags)}"
        text += f"\n<b>{lang.page}s</b>: <code>{manga['pages']}</code>"

        results.append(
            InlineQueryResultPhoto(
                photo_url=str(manga["photo"]),
                title=manga["title"],
                caption=text,
                description=manga["tags"],
                reply_markup=ikb(
                    [
                        [
                            (
                                "👠 nHentai",
                                f"https://nhentai.net/g/{manga['id']}",
                                "url",
                            ),
                            (lang.read_button, manga["url"], "url"),
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
    nhentai = await get_nhentai_by_id(id=m_id)

    if nhentai is None:
        artist, photo, title, pages, tags, url = (None,) * 6

        tgph = Telegraph()
        await tgph.create_account(
            short_name="Gojira",
            author_name="@PyGodzillaBot",
            author_url="https://t.me/PyGodzillaBot",
        )

        html_content = ""
        async with httpx.AsyncClient(http2=True) as client:
            response = await client.get(f"https://nhentai.net/api/gallery/{m_id}")
            while not response.status_code == 200:
                await asyncio.sleep(0.5)
                response = await client.get(f"https://nhentai.net/api/gallery/{m_id}")

            res = response.json()
            pages = res["images"]["pages"]
            info = res["tags"]
            title = res["title"]["english"]
            links: List = []
            tags: List = []
            artist = ""
            total_pages = res["num_pages"]
            extensions = {"j": "jpg", "p": "png", "g": "gif"}
            for i, x in enumerate(pages):
                media_id = res["media_id"]
                temp = x["t"]
                file = f"{i+1}.{extensions[temp]}"
                photo = f"https://i.nhentai.net/galleries/{media_id}/{file}"
                links.append(photo)

            for i in info:
                if i["type"] == "tag":
                    tag = i["name"]
                    tags.append(tag)
                if i["type"] == "artist":
                    artist = f"{i['name']}"

            tags = ", ".join(tags)
            html_content = "".join(f"<img src={link}><br>" for link in links)

            await client.aclose()

        page = await tgph.create_page(
            title=title,
            html_content=html_content,
            author_name="@PyGodzillaBot",
            author_url="https://t.me/PyGodzillaBot",
        )
        url = page["url"]

        await create_nhentai(
            id=m_id,
            artist=artist,
            photo=photo,
            title=title,
            pages=total_pages,
            tags=tags,
            url=url,
        )
        nhentai = await get_nhentai_by_id(id=m_id)

    return nhentai
