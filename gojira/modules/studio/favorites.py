# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>

import httpx
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.nav import Pagination
from pyrogram.types import CallbackQuery

from gojira.bot import Gojira
from gojira.database.favorites import filter_user_favorites
from gojira.modules.studio.utils import Studio
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_callback_query(filters.regex(r"favorites studio (?P<page>\d+)"))
@use_chat_language()
async def studio_favorites(bot: Gojira, callback: CallbackQuery):
    page = int(callback.matches[0]["page"])

    message = callback.message
    user = callback.from_user
    lang = callback._lang

    keyboard = []
    async with httpx.AsyncClient(http2=True) as client:
        favorites = await filter_user_favorites(user=user.id, type="studio")

        results = []
        for favorite in favorites:
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
                        id=favorite["item"],
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

            results.append((favorite, studio))

        layout = Pagination(
            results,
            item_data=lambda i, pg: f"studio {i[0]['item']}",
            item_title=lambda i, pg: i[1].name,
            page_data=lambda pg: f"favorites studio {pg}",
        )

        lines = layout.create(page, lines=8)

        if len(lines) > 0:
            keyboard += lines

    keyboard.append([(lang.back_button, "studio")])

    await message.edit_text(
        lang.favorites_text,
        reply_markup=ikb(keyboard),
    )
