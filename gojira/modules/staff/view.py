# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>

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


@Gojira.on_message(filters.cmd(r"staff (.+)"))
@Gojira.on_callback_query(filters.regex(r"^staff (\d+)\s?(\d+)?\s?(\d+)?"))
@use_chat_language()
async def staff_view(bot: Gojira, union: Union[Message, CallbackQuery]):
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
                return

        is_search = union.matches[0].group(3)
        if bool(is_search) and not is_private:
            await message.delete()

    if not bool(query):
        return

    async with anilist.AsyncClient() as client:
        if not query.isdecimal():
            results = await client.search(query, "staff", page=1, limit=10)
            if results is None:
                await asyncio.sleep(0.5)
                results = await client.search(query, "staff", page=1, limit=10)

            if results is None or len(results) == 0:
                return

            if len(results) == 1:
                staff_id = results[0].id
            else:
                keyboard = []
                for result in results:
                    keyboard.append(
                        [(result.name.full, f"staff {result.id} {user.id} 1")]
                    )
                await message.reply_text(
                    lang.search_results_text(
                        query=query,
                    ),
                    reply_markup=ikb(keyboard),
                )
                return
        else:
            staff_id = int(query)

        staff = await client.get(staff_id, "staff")

        if staff is None:
            return

        text = f"<b>{staff.name.full}</b>"
        text += f"\n<b>ID</b>: <code>{staff.id}</code>"
        if hasattr(staff, "language"):
            text += f"\n<b>{lang.language}</b>: <code>{staff.language}</code>"
        if hasattr(staff, "favorites"):
            text += f"\n<b>{lang.favorite}s</b>: <code>{staff.favorites}</code>"
        if hasattr(staff, "description"):
            text += f"\n\n{staff.description}"

        photo: str = ""
        if hasattr(staff, "image"):
            if hasattr(staff.image, "large"):
                photo = staff.image.large
            elif hasattr(staff.image, "medium"):
                photo = staff.image.medium

        buttons = [("🐢 Anilist", staff.url, "url")]

        if is_private:
            buttons.append(await get_favorite_button(lang, user, "staff", staff.id))

        keyboard = array_chunk(buttons, 2)

        if len(text) > 1024:
            text = text[:1021] + "..."

        # Markdown
        text = text.replace("__", "**")
        text = text.replace("~", "~~")

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
