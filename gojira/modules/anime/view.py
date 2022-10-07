# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
import math
from typing import Union

import anilist
import httpx
import humanize
import numpy
from pyrogram import filters
from pyrogram.helpers import array_chunk, ikb
from pyrogram.types import CallbackQuery, InputMediaPhoto, Message

from gojira.bot import Gojira
from gojira.modules.favorites import get_favorite_button
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"anime (.+)"))
@Gojira.on_callback_query(filters.regex(r"^anime (\d+)\s?(\d+)?\s?(\d+)?"))
@use_chat_language()
async def anime_view(bot: Gojira, union: Union[CallbackQuery, Message]):
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
            results = await client.search(query, "anime", page=1, limit=10)
            if results is None:
                await asyncio.sleep(0.5)
                results = await client.search(query, "anime", page=1, limit=10)

            if results is None or len(results) == 0:
                await message.reply_text(lang.no_results_text)
                return

            if len(results) == 1:
                anime_id = results[0].id
            else:
                keyboard = []
                for result in results:
                    keyboard.append(
                        [(result.title.romaji, f"anime {result.id} {user.id} 1")]
                    )
                await message.reply_text(
                    lang.search_results_text(
                        query=query,
                    ),
                    reply_markup=ikb(keyboard),
                )
                return
        else:
            anime_id = int(query)

        anime = await client.get(anime_id, "anime")

        if anime is None:
            await union.answer(
                lang.no_results_text,
                show_alert=True,
                cache_time=60,
            )
            return

        text = f"<b>{anime.title.romaji}</b>"
        if hasattr(anime.title, "native"):
            text += f" (<code>{anime.title.native}</code>)"
        text += f"\n\n<b>ID</b>: <code>{anime.id}</code>"
        if hasattr(anime, "score") and hasattr(anime.score, "average"):
            text += f"\n<b>{lang.score}</b>: <code>{anime.score.average}</code>"
        text += f"\n<b>{lang.status}</b>: <code>{anime.status}</code>"
        if hasattr(anime, "genres"):
            text += f"\n<b>{lang.genres}</b>: <code>{', '.join(anime.genres)}</code>"
        if hasattr(anime, "studios"):
            text += f"\n<b>{lang.studios}</b>: <code>{', '.join(anime.studios)}</code>"
        if hasattr(anime, "format"):
            text += f"\n<b>{lang.format}</b>: <code>{anime.format}</code>"
        if hasattr(anime, "duration"):
            text += f"\n<b>{lang.duration}</b>: <code>{anime.duration}m</code>"
        if not anime.format == "MOVIE" and hasattr(anime, "episodes"):
            text += f"\n<b>{lang.episode}s</b>: <code>{anime.episodes}</code>"
        if not anime.status == "NOT_YET_RELEASED":
            text += f"\n<b>{lang.start_date}</b>: <code>{anime.start_date.day if hasattr(anime.start_date, 'day') else 0}/{anime.start_date.month if hasattr(anime.start_date, 'month') else 0}/{anime.start_date.year if hasattr(anime.start_date, 'year') else 0}</code>"
        if anime.status not in ["NOT_YET_RELEASED", "RELEASING"]:
            text += f"\n<b>{lang.end_date}</b>: <code>{anime.end_date.day if hasattr(anime.end_date, 'day') else 0}/{anime.end_date.month if hasattr(anime.end_date, 'month') else 0}/{anime.end_date.year if hasattr(anime.end_date, 'year') else 0}</code>"

        buttons = [
            (lang.view_more_button, f"anime more {anime.id} {user.id}"),
        ]

        if is_private:
            buttons.append(await get_favorite_button(lang, user, "anime", anime.id))

        keyboard = array_chunk(buttons, 2)

        if hasattr(anime, "relations"):
            relations_buttons = []
            for relation in anime.relations:
                if relation[0] in ["PREQUEL", "SEQUEL"]:
                    relations_buttons.append(
                        (
                            lang.strings[lang.code][f"{relation[0].lower()}_button"],
                            f"anime {relation[1].id} {user.id}",
                        )
                    )
            if len(relations_buttons) > 0:
                if not relations_buttons[0][0] == lang.prequel_button:
                    relations_buttons = relations_buttons[::-1]
                keyboard.append(relations_buttons)

        photo = f"https://img.anili.st/media/{anime_id}"

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


@Gojira.on_callback_query(filters.regex(r"^anime more (\d+) (\d+)"))
@use_chat_language()
async def anime_view_more(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    user = callback.from_user
    lang = callback._lang

    anime_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))

    if user_id != user.id:
        await callback.answer(
            lang.button_not_for_you,
            show_alert=True,
            cache_time=60,
        )
        return

    async with anilist.AsyncClient() as client:
        anime = await client.get(anime_id, "anime")

        buttons = [
            (lang.description_button, f"anime description {anime_id} {user_id} 1"),
            (lang.characters_button, f"anime characters {anime_id} {user_id}"),
            (lang.staff_button, f"anime staff {anime_id} {user_id} 1"),
            (lang.airing_button, f"anime airing {anime_id} {user_id}"),
        ]

        if hasattr(anime, "trailer") and hasattr(anime.trailer, "url"):
            buttons.append((lang.trailer_button, anime.trailer.url, "url"))

        buttons.append(("🐢 Anilist", anime.url, "url"))

        keyboard = array_chunk(buttons, 2)

        keyboard.append([(lang.back_button, f"anime {anime_id} {user_id}")])

        await message.edit_text(
            lang.view_more_text,
            reply_markup=ikb(keyboard),
        )


@Gojira.on_callback_query(filters.regex(r"anime description (\d+) (\d+) (\d+)"))
@use_chat_language()
async def anime_view_description(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    user = callback.from_user
    lang = callback._lang

    anime_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))
    page = int(callback.matches[0].group(3))

    if user_id != user.id:
        await callback.answer(
            lang.button_not_for_you,
            show_alert=True,
            cache_time=60,
        )
        return

    async with anilist.AsyncClient() as client:
        anime = await client.get(anime_id, "anime")

        if not hasattr(anime, "description"):
            await callback.answer(
                lang.no_description_text,
                show_alert=True,
                cache_time=60,
            )
            return

        description = anime.description
        amount = 1024
        page = 1 if page <= 0 else page
        offset = (page - 1) * amount
        stop = offset + amount
        pages = math.ceil(len(description) / amount)
        description = description[offset - (3 if page > 1 else 0) : stop]

        page_buttons = []
        if page > 1:
            page_buttons.append(
                ("⬅️", f"anime description {anime_id} {user_id} {page - 1}")
            )
        if not page == pages:
            description = description[: len(description) - 3] + "..."
            page_buttons.append(
                ("➡️", f"anime description {anime_id} {user_id} {page + 1}")
            )

        keyboard = []
        if len(page_buttons) > 0:
            keyboard.append(page_buttons)

        keyboard.append([(lang.back_button, f"anime more {anime_id} {user_id}")])

        await message.edit_text(
            description,
            reply_markup=ikb(keyboard),
        )


@Gojira.on_callback_query(filters.regex(r"^anime characters (\d+) (\d+)"))
@use_chat_language()
async def anime_view_characters(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    user = callback.from_user
    lang = callback._lang

    anime_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))

    if user_id != user.id:
        await callback.answer(
            lang.button_not_for_you,
            show_alert=True,
            cache_time=60,
        )
        return

    async with anilist.AsyncClient() as client:
        anime = await client.get(anime_id, "anime")

        keyboard = [
            [
                (lang.back_button, f"anime more {anime_id} {user_id}"),
            ],
        ]

        if not hasattr(anime, "characters"):
            await callback.answer(
                lang.no_results_text,
                show_alert=True,
                cache_time=60,
            )
            return

        text = lang.characters_text

        characters = sorted(anime.characters, key=lambda character: character.id)
        for character in characters:
            text += f"\n• <code>{character.id}</code> - <a href='https://t.me/{bot.me.username}/?start=character_{character.id}'>{character.name.full}</a> (<i>{character.role}</i>)"

        await message.edit_text(
            text,
            reply_markup=ikb(keyboard),
        )


@Gojira.on_callback_query(filters.regex(r"^anime staff (\d+) (\d+) (\d+)"))
@use_chat_language()
async def anime_view_staff(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    user = callback.from_user
    lang = callback._lang

    anime_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))
    page = int(callback.matches[0].group(3))

    if user_id != user.id:
        await callback.answer(
            lang.button_not_for_you,
            show_alert=True,
            cache_time=60,
        )
        return

    async with anilist.AsyncClient() as client:
        anime = await client.get(anime_id, "anime")

        if not hasattr(anime, "staff"):
            await callback.answer(
                lang.no_results_text,
                show_alert=True,
                cache_time=60,
            )
            return

        staff_text = lang.staff_text

        staffs = sorted(anime.staff, key=lambda staff: staff.id)
        for person in staffs:
            staff_text += f"\n• <code>{person.id}</code> - <a href='https://t.me/{bot.me.username}/?start=staff_{person.id}'>{person.name.full}</a> (<i>{person.role}</i>)"

        # Separate staff_text into pages of 8 items
        staff_text = numpy.array(staff_text.split("\n"))
        staff_text = numpy.split(staff_text, numpy.arange(8, len(staff_text), 8))

        pages = len(staff_text)
        page = 1 if page <= 0 else page

        page_buttons = []
        if page > 1:
            page_buttons.append(("⬅️", f"anime staff {anime_id} {user_id} {page - 1}"))
        if not page + 1 == pages:
            page_buttons.append(("➡️", f"anime staff {anime_id} {user_id} {page + 1}"))

        staff_text = staff_text[page].tolist()
        staff_text = "\n".join(staff_text)

        keyboard = []
        if len(page_buttons) > 0:
            keyboard.append(page_buttons)

        keyboard.append([(lang.back_button, f"anime more {anime_id} {user_id}")])

        await message.edit_text(
            staff_text,
            reply_markup=ikb(keyboard),
        )


@Gojira.on_callback_query(filters.regex(r"^anime airing (\d+) (\d+)"))
@use_chat_language()
async def anime_view_airing(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    user = callback.from_user
    lang = callback._lang

    anime_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))

    if user_id != user.id:
        await callback.answer(
            lang.button_not_for_you,
            show_alert=True,
            cache_time=60,
        )
        return

    async with anilist.AsyncClient() as client:
        anime = await client.get(anime_id)

    text = f"{lang.airing_text}\n"
    if hasattr(anime, "next_airing"):
        airing_time = anime.next_airing.time_until
        text += f"<b>{lang.episode}:</b> <code>{anime.next_airing.episode}</code>\n"
        text += (
            f"<b>{lang.airing}:</b> <code>{humanize.precisedelta(airing_time)}</code>"
        )
    else:
        episodes = anime.episodes if hasattr(anime, "episodes") else "N/A"
        text += f"<b>{lang.episode}:</b> <code>{episodes}</code>\n"
        text += f"<b>{lang.airing}:</b> <code>N/A</code>"

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(
            url="https://graphql.anilist.co",
            json=dict(
                query="""
                query($id: Int) {
                    Page(page: 1, perPage: 1) {
                        media(id: $id, type: ANIME) {
                            externalLinks {
                                id
                                url
                                site
                                type
                            }
                        }
                    }
                }
                """,
                variables=dict(
                    id=int(anime_id),
                ),
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        data = response.json()
        await client.aclose()
        buttons = []
        if data["data"]:
            externalLinks = data["data"]["Page"]["media"][0]["externalLinks"]
            for link in externalLinks:
                if link["type"] == "STREAMING":
                    buttons.append((link["site"], link["url"], "url"))

    keyboard = array_chunk(buttons, 3)

    keyboard.append([(lang.back_button, f"anime more {anime_id} {user_id}")])

    await message.edit_text(
        text,
        reply_markup=ikb(keyboard),
    )
