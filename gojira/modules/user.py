# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>

import asyncio
import time
from datetime import datetime
from typing import Union

import anilist
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, InputMediaPhoto, Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"user (.+)"))
@Gojira.on_callback_query(filters.regex(r"^user (\d+)\s?(\d+)?\s?(\d+)?"))
@use_chat_language()
async def user_view(bot: Gojira, union: Union[Message, CallbackQuery]):
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
        if not is_callback:
            results = await client.search(query, "user", page=1, limit=10)
            if results is None:
                await asyncio.sleep(0.5)
                results = await client.search(query, "user", page=1, limit=10)

            if results is None or len(results) == 0:
                return

            if len(results) == 1:
                query = results[0].name
            else:
                keyboard = []
                for result in results:
                    keyboard.append([(result.name, f"user {result.name} {user.id} 1")])
                await message.reply_text(
                    lang.search_results_text(
                        query=query,
                    ),
                    reply_markup=ikb(keyboard),
                )
        else:
            query = str(query)

        auser = await client.get(query, "user")

        if auser is None:
            return

        text = f"<b>{auser.name}</b> (<code>{auser.id}</code>)\n\n"
        text += f"<b>{lang.anime_stats}</b>:\n"
        text += (
            f"{lang.total_anime_watched}: <code>{auser.statistics.anime.count}</code>\n"
        )
        text += f"{lang.total_episode_watched}: <code>{auser.statistics.anime.episodes_watched}</code>\n"
        text += f"{lang.total_time_spent}: <code>{auser.statistics.anime.minutes_watched}</code>\n"
        text += f"{lang.average_score}: <code>{auser.statistics.anime.mean_score}</code>\n\n"
        text += f"<b>{lang.manga_stats}</b>:\n"
        text += (
            f"{lang.total_manga_read}: <code>{auser.statistics.manga.count}</code>\n"
        )
        text += f"{lang.total_chapters_read}: <code>{auser.statistics.manga.chapters_read}</code>\n"
        text += f"{lang.total_volumes_read}: <code>{auser.statistics.manga.volumes_read}</code>\n"
        text += f"{lang.average_score}: <code>{auser.statistics.manga.mean_score}</code>\n\n"
        text += f"<b>{lang.created_at}</b>: <code>{datetime.fromtimestamp(auser.created_at.timestamp)}</code>\n"
        text += f"<b>{lang.updated_at}</b>: <code>{datetime.fromtimestamp(auser.updated_at.timestamp)}</code>"

        keyboard = [[("🐢 Anilist", auser.url, "url")]]

        photo = f"https://img.anili.st/user/{auser.id}?a={time.time()}"

        if bool(message.photo) and is_callback:
            await union.edit_message_media(
                InputMediaPhoto(
                    photo,
                    caption=text,
                ),
                reply_markup=ikb(keyboard),
            )
        elif bool(message.photo) and not bool(message.via_bot):
            await message.edit_text(
                text,
                reply_markup=ikb(keyboard),
            )
        else:
            await message.reply_photo(
                photo,
                caption=text,
                reply_markup=ikb(keyboard),
            )
