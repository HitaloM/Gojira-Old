# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import os
from datetime import timedelta

import httpx
from pyrogram import filters
from pyrogram.errors import BadRequest
from pyrogram.helpers import bki, ikb
from pyrogram.types import Document, InputMediaPhoto, Message, Video

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"scan$") & filters.reply)
@use_chat_language()
async def anime_scan(bot: Gojira, message: Message):
    reply = message.reply_to_message
    user = message.from_user
    lang = message._lang

    if user.id == bot.me.id:
        return

    if not reply.media:
        await message.reply_text(lang.media_not_found_text)
        return

    media = (
        reply.photo or reply.sticker or reply.animation or reply.document or reply.video
    )

    if isinstance(media, (Document, Video)):
        if bool(media.thumbs) and len(media.thumbs) > 0:
            media = media.thumbs[0]
        else:
            return

    sent = await message.reply_photo(
        "https://i.imgur.com/m0N2pFc.jpg", caption=lang.scanning_media_text
    )

    path = await bot.download_media(media)

    async with httpx.AsyncClient(http2=True) as client:
        try:
            response = await client.post(
                "https://api.trace.moe/search?anilistInfo&cutBorders",
                files=dict(image=open(path, "rb")),
                timeout=20.0,
            )
        except httpx.TimeoutException:
            await sent.edit_text(lang.timed_out_text)
            return

        if response.status_code == 200:
            pass
        elif response.status_code == 429:
            await sent.edit_text(lang.api_overuse_text)
            return
        else:
            await sent.edit_text(lang.api_down_text)
            return

        data = response.json()
        results = data["result"]
        if len(results) == 0:
            await sent.edit_text(lang.no_results_text)
            return

        result = results[0]

        video = result["video"]
        to_time = result["to"]
        episode = result["episode"]
        anilist_id = result["anilist"]["id"]
        file_name = result["filename"]
        from_time = result["from"]
        similarity = result["similarity"]
        is_adult = result["anilist"]["isAdult"]
        title_native = result["anilist"]["title"]["native"]
        title_romaji = result["anilist"]["title"]["romaji"]

        text = f"<b>{title_romaji}</b>"
        if title_native:
            text += f" (<code>{title_native}</code>)"
        text += f"\n\n<b>ID</b>: <code>{anilist_id}</code>"
        if episode:
            text += f"\n<b>{lang.episode}</b>: <code>{episode}</code>"
        if is_adult:
            text += f"\n<b>{lang.is_adult}</b>: <code>{lang.yes_text}</code>"
        text += (
            f"\n<b>{lang.similarity}</b>: <code>{round(similarity * 100, 2)}%</code>"
        )

        sent = await sent.edit_media(
            InputMediaPhoto(
                f"https://img.anili.st/media/{anilist_id}",
                text,
            ),
            reply_markup=ikb(
                [
                    [
                        (lang.view_more_button, f"anime {anilist_id} {user.id}"),
                    ]
                ]
            ),
        )

        from_time = (
            str(timedelta(seconds=result["from"])).split(".", 1)[0].rjust(8, "0")
        )
        to_time = str(timedelta(seconds=result["to"])).split(".", 1)[0].rjust(8, "0")

        if video is not None:
            try:
                sent_video = await sent.reply_video(
                    video=f"{video}&size=l",
                    caption=f"<code>{file_name}</code>\n\n<code>{from_time}</code> - <code>{to_time}</code>",
                )

                keyboard = bki(sent.reply_markup)
                keyboard[0].append(("📹 Preview", sent_video.link, "url"))
                await sent.edit_reply_markup(
                    reply_markup=ikb(keyboard),
                )
            except BadRequest:
                pass

        await client.aclose()

    os.remove(path)
