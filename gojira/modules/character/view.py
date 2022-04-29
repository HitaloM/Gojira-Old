# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
from typing import Union

import anilist
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.helpers import array_chunk, ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.modules.favorites import get_favorite_button
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"character (.+)"))
@Gojira.on_callback_query(filters.regex(r"^character (\d+)\s?(\d+)?\s?(\d+)?"))
@use_chat_language()
async def character_view(bot: Gojira, union: Union[CallbackQuery, Message]):
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

    async with anilist.AsyncClient() as client:
        if not query.isdecimal():
            results = await client.search(query, "character", page=1, limit=10)
            if results is None:
                await asyncio.sleep(0.5)
                results = await client.search(query, "character", page=1, limit=10)

            if results is None or len(results) == 0:
                return

            if len(results) == 1:
                character_id = results[0].id
            else:
                keyboard = []
                for result in results:
                    keyboard.append(
                        [(result.name.full, f"character {result.id} {user.id} 1")]
                    )
                await message.reply_text(
                    lang.search_results_text(
                        query=query,
                    ),
                    reply_markup=ikb(keyboard),
                )
                return
        else:
            character_id = int(query)

        character = await client.get(character_id, "character")

        if character is None:
            return

        text = f"<b>{character.name.full}</b>"
        text += f"\n<b>ID</b>: <code>{character.id}</code>"
        if hasattr(character, "favorites"):
            text += f"\n<b>{lang.favorite}s</b>: <code>{character.favorites}</code>"
        if hasattr(character, "description"):
            text += f"\n\n{character.description}"

        photo: str = ""
        if hasattr(character, "image"):
            if hasattr(character.image, "large"):
                photo = character.image.large
            elif hasattr(character.image, "medium"):
                photo = character.image.medium

        buttons = [("🐢 Anilist", character.url, "url")]

        if is_private:
            buttons.append(
                await get_favorite_button(lang, user, "character", character.id)
            )

        keyboard = array_chunk(buttons, 2)

        if len(text) > 1024:
            text = text[:1021] + "..."

        # Markdown
        text = text.replace("__", "**")
        text = text.replace("~", "||")

        if len(photo) > 0:
            await message.reply_photo(
                photo=photo,
                caption=text,
                parse_mode=ParseMode.DEFAULT,
                reply_markup=ikb(keyboard),
            )
        else:
            await message.reply_text(
                text=text,
                parse_mode=ParseMode.DEFAULT,
                reply_markup=ikb(keyboard),
            )
