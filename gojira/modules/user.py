# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>

import time
from datetime import datetime

import anilist
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"user (.+)"))
@use_chat_language()
async def user_view(bot: Gojira, message: Message):
    lang = message._lang
    query = message.matches[0].group(1)

    if not bool(query):
        return

    async with anilist.AsyncClient() as client:
        try:
            user = await client.get(query, "user")
        except TypeError:
            return

        if user is None:
            return

    text = f"<b>{user.name}</b> (<code>{user.id}</code>)\n\n"
    text += f"<b>{lang.anime_stats}</b>:\n"
    text += f"{lang.total_anime_watched}: <code>{user.statistics.anime.count}</code>\n"
    text += f"{lang.total_episode_watched}: <code>{user.statistics.anime.episodes_watched}</code>\n"
    text += f"{lang.total_time_spent}: <code>{user.statistics.anime.minutes_watched}</code>\n"
    text += f"{lang.average_score}: <code>{user.statistics.anime.mean_score}</code>\n\n"
    text += f"<b>{lang.manga_stats}</b>:\n"
    text += f"{lang.total_manga_read}: <code>{user.statistics.manga.count}</code>\n"
    text += f"{lang.total_chapters_read}: <code>{user.statistics.manga.chapters_read}</code>\n"
    text += f"{lang.total_volumes_read}: <code>{user.statistics.manga.volumes_read}</code>\n"
    text += f"{lang.average_score}: <code>{user.statistics.manga.mean_score}</code>\n\n"
    text += f"<b>{lang.created_at}</b>: <code>{datetime.fromtimestamp(user.created_at.timestamp)}</code>\n"
    text += f"<b>{lang.updated_at}</b>: <code>{datetime.fromtimestamp(user.updated_at.timestamp)}</code>"

    keyboard = [[("🐢 Anilist", user.url, "url")]]

    await message.reply_photo(
        photo=f"https://img.anili.st/user/{user.id}?a={time.time()}",
        caption=text,
        parse_mode="combined",
        reply_markup=ikb(keyboard),
    )
