# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>

from typing import Union

import httpx
from pyrogram import filters
from pyrogram.helpers import array_chunk, ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.modules.favorites import get_favorite_button
from gojira.modules.studio.utils import Studio
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"studio (.+)"))
@Gojira.on_callback_query(filters.regex(r"^studio (\d+)\s?(\d+)?\s?(\d+)?"))
@use_chat_language()
async def studio_view(bot: Gojira, union: Union[CallbackQuery, Message]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    lang = union._lang

    is_private = await filters.private(bot, message)

    query = union.matches[0].group(1)

    if is_callback:
        user_id = union.matches[0].group(2)
        if user_id is not None:
            user_id = int(user_id)

            if user_id != user.id:
                await union.answer(
                    lang.button_not_for_you,
                    show_alert=True,
                    cache_time=60,
                )
                return

        is_search = union.matches[0].group(3)
        if bool(is_search) and not is_private:
            await message.delete()

    if not bool(query):
        return

    if is_callback:
        user_id = union.matches[0].group(2)
        if user_id is not None:
            user_id = int(user_id)

            if user_id != user.id:
                await union.answer(
                    lang.button_not_for_you,
                    show_alert=True,
                    cache_time=60,
                )
                return

        is_search = union.matches[0].group(3)
        if bool(is_search) and not is_private:
            await message.delete()

    if not bool(query):
        return

    async with httpx.AsyncClient(http2=True) as client:
        if not query.isdecimal():
            response = await client.post(
                url="https://graphql.anilist.co",
                json=dict(
                    query="""
                    query($search: String) {
                        Page(page: 1, perPage: 10) {
                            studios(search: $search, sort: SEARCH_MATCH) {
                                id
                                name
                            }
                        }
                    }
                    """,
                    variables=dict(
                        search=str(query),
                    ),
                ),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            data = response.json()

            items = data["data"]["Page"]["studios"]

            results = [
                Studio(
                    id=item["id"],
                    name=item["name"],
                    url=None,
                    favorites=None,
                    is_animation_studio=None,
                )
                for item in items
            ]

            if results is None or len(results) == 0:
                await message.reply_text(lang.no_results_text)
                return

            if len(results) == 1:
                query = results[0].id
            else:
                keyboard = []
                for result in results:
                    keyboard.append([(result.name, f"studio {result.id} {user.id} 1")])
                await message.reply_text(
                    lang.search_results_text(
                        query=query,
                    ),
                    reply_markup=ikb(keyboard),
                )
                return
        else:
            query = int(query)

        response = await client.post(
            url="https://graphql.anilist.co",
            json=dict(
                query="""
                query($id: Int) {
                    Studio(id: $id) {
                        id
                        name
                        siteUrl
                        favourites
                        isAnimationStudio
                        media(sort: POPULARITY_DESC) {
                            nodes {
                                id
                                title {
                                    romaji
                                    english
                                    native
                                    }
                                type
                                }
                            }
                        }
                    }
                """,
                variables=dict(
                    id=int(query),
                ),
            ),
        )
        data = response.json()

        item = data["data"]["Studio"]
        studio = Studio(
            id=item["id"],
            name=item["name"],
            url=item["siteUrl"],
            favorites=item["favourites"],
            is_animation_studio=item["isAnimationStudio"],
        )

        if studio is None:
            await union.answer(
                lang.no_results_text,
                show_alert=True,
                cache_time=60,
            )
            return

        text = f"<b>{studio.name}</b>"
        text += f"\n<b>ID</b>: <code>{studio.id}</code>"
        text += f"\n<b>{lang.favorite}</b>: <code>{studio.favorites}</code>"
        is_anim = lang.yes_text if studio.is_animation_studio else lang.no_text
        text += f"\n<b>{lang.is_animation_studio}</b>: <code>{is_anim}</code>"

        buttons = [("🐢 Anilist", studio.url, "url")]

        if is_private:
            buttons.append(await get_favorite_button(lang, user, "studio", studio.id))

        keyboard = array_chunk(buttons, 2)

        await message.reply_text(text, reply_markup=ikb(keyboard))

    await client.aclose()
