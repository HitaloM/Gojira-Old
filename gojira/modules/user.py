# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>

import asyncio
import time
from datetime import datetime
from typing import Union

import anilist
import httpx
from anilist.types import Statistic, User
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
        if not is_callback:
            results = await client.search(query, "user", page=1, limit=10)
            if results is None:
                await asyncio.sleep(0.5)
                results = await client.search(query, "user", page=1, limit=10)

            if results is None or len(results) == 0:
                await message.reply_text(lang.no_results_text)
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
                return
        else:
            query = str(query)

        async with httpx.AsyncClient(http2=True) as client:
            response = await client.post(
                url="https://graphql.anilist.co",
                json=dict(
                    query="""
                    query ($name: String) {
                        User(name: $name) {
                            id
                            name
                            about
                            siteUrl
                            donatorTier
                            createdAt
                            updatedAt
                        }
                    }
                    """,
                    variables=dict(
                        name=query,
                    ),
                ),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            data = response.json()
            await client.aclose()

        item = data["data"]["User"]
        auser = User(
            id=item["id"],
            name=item["name"],
            created_at=item["createdAt"],
            updated_at=item["updatedAt"],
            about=item["about"],
            url=item["siteUrl"],
            donator_tier=item["donatorTier"],
        )

        if auser is None:
            await union.answer(
                lang.no_results_text,
                show_alert=True,
                cache_time=60,
            )
            return

        text = f"<b>{lang.username}</b>: <code>{auser.name}</code>\n"
        text += f"<b>ID</b>: <code>{auser.id}</code>\n"
        text += f"<b>{lang.donator}</b>: <code>{lang.yes_text if hasattr(auser, 'donator_tier') else lang.no_text}</code>\n"
        if hasattr(auser, "about"):
            if len(auser.about) > 200:
                auser.about = auser.about[0:200] + "..."
            text += f"<b>{lang.bio}</b>: <code>{auser.about}</code>\n"

        text += f"\n<b>{lang.created_at}</b>: <code>{datetime.fromtimestamp(auser.created_at.timestamp)}</code>\n"
        text += f"<b>{lang.updated_at}</b>: <code>{datetime.fromtimestamp(auser.updated_at.timestamp)}</code>"

        keyboard = [
            [
                (lang.anime_stats, f"user stats {auser.name} anime"),
                (lang.manga_stats, f"user stats {auser.name} manga"),
            ],
            [("🐢 Anilist", auser.url, "url")],
        ]

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


@Gojira.on_callback_query(filters.regex(r"^user stats (.+) (.+)"))
@use_chat_language()
async def user_stats_view(bot: Gojira, callback: CallbackQuery):
    lang = callback._lang
    user_name = str(callback.matches[0].group(1))
    stat_type = str(callback.matches[0].group(2))

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(
            url="https://graphql.anilist.co",
            json=dict(
                query="""
                query ($name: String) {
                    User(name: $name) {
                        id
                        name
                    statistics {
                        anime {
                            count
                            meanScore
                            minutesWatched
                            episodesWatched
                            }
                        manga {
                            count
                            meanScore
                            chaptersRead
                             volumesRead
                           }
                        }
                    }
                }
                """,
                variables=dict(
                    name=user_name,
                ),
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        data = response.json()
        await client.aclose()

        if data["data"]:
            item = data["data"]["User"]

            if stat_type == "anime":
                stat_anime = item["statistics"]["anime"]
                anime = Statistic(
                    count=stat_anime["count"],
                    mean_score=stat_anime["meanScore"],
                    minutes_watched=stat_anime["minutesWatched"],
                    episodes_watched=stat_anime["episodesWatched"],
                )

                text = f"{lang.total_anime_watched}: {anime.count}\n"
                text += f"{lang.total_episode_watched}: {anime.episodes_watched}\n"
                text += f"{lang.total_time_spent}: {anime.minutes_watched}\n"
                text += f"{lang.average_score}: {anime.mean_score}"
            else:
                stat_manga = item["statistics"]["manga"]
                manga = Statistic(
                    count=stat_manga["count"],
                    mean_score=stat_manga["meanScore"],
                    chapters_read=stat_manga["chaptersRead"],
                    volumes_read=stat_manga["volumesRead"],
                )

                text = f"{lang.total_manga_read}: {manga.count}\n"
                text += f"{lang.total_chapters_read}: {manga.chapters_read}\n"
                text += f"{lang.total_volumes_read}: {manga.volumes_read}\n"
                text += f"{lang.average_score}: {manga.mean_score}"

            await callback.answer(text, show_alert=True, cache_time=60)
