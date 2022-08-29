# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>
# SOFTWARE.

from typing import Tuple

from pyrogram import filters
from pyrogram.helpers import bki, ikb
from pyrogram.types import CallbackQuery, User

from gojira.bot import Gojira
from gojira.database.favorites import (
    create_user_favorite,
    delete_user_favorite,
    get_user_favorites,
)
from gojira.utils.langs.decorators import use_chat_language


async def get_favorite_button(
    lang, user: User, content_type: str, content_id: int
) -> Tuple:
    favorite = await get_user_favorites(
        user=user.id, item=content_id, type=content_type
    )
    if favorite is None:
        status = "⭐"
    else:
        status = "🌟"
    return (f"{status} {lang.favorite}", f"favorite {content_type} {content_id}")


@Gojira.on_callback_query(filters.regex(r"^favorite (?P<type>\w+) (?P<id>\d+)"))
@use_chat_language()
async def favorite_callback(bot: Gojira, callback: CallbackQuery):
    content_type = callback.matches[0]["type"]
    content_id = int(callback.matches[0]["id"])
    message = callback.message
    user = callback.from_user
    lang = callback._lang

    favorite = await get_user_favorites(
        user=user.id, item=content_id, type=content_type
    )

    if favorite is None:
        await create_user_favorite(user=user.id, item=content_id, type=content_type)
        await callback.answer(lang.added_to_favorites_alert, show_alert=True)
    else:
        await delete_user_favorite(user=user.id, item=content_id, type=content_type)
        await callback.answer(lang.removed_from_favorites_alert, show_alert=True)

    keyboard = bki(message.reply_markup)

    for line, column in enumerate(keyboard):
        for index, button in enumerate(column):
            if button[1].startswith("favorite"):
                keyboard[line][index] = await get_favorite_button(
                    lang, user, content_type, content_id
                )

    await callback.edit_message_reply_markup(ikb(keyboard))
