# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
from typing import List

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Animation, Document, Message, Photo, Sticker, Video

from gojira.bot import Gojira
from gojira.config import CHATS
from gojira.database.chats import filter_chats_by_language
from gojira.database.users import filter_users_by_language
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"broadcast (\w+) (\w+)") & filters.sudo)
@use_chat_language()
async def broadcast(bot: Gojira, message: Message):
    reply = message.reply_to_message
    lang = message._lang

    to = message.matches[0].group(1)
    language = message.matches[0].group(2)

    media = message.photo or message.animation or message.document or message.video
    text = " ".join((message.text or message.caption).split()[3:])
    if bool(reply):
        media = (
            reply.photo
            or reply.sticker
            or reply.animation
            or reply.document
            or reply.video
        )
        text = reply.text or reply.caption

    if not media:
        if text is None or len(text) == 0:
            await message.reply_text(lang.empty_message_text)
            return

    chats = []
    if to in ["groups", "all"]:
        chats += [
            chat["id"] for chat in await filter_chats_by_language(language=language)
        ]
    if to in ["users", "all"]:
        chats += [
            user["id"] for user in await filter_users_by_language(language=language)
        ]

    if len(chats) == 0:
        await message.reply_text(lang.no_chat_found_text)
    else:
        sent = await message.reply_text(lang.sending_alert_text)

        success: List = []
        failed: List = []
        for chat in chats:
            if chat in CHATS.values():
                continue

            try:
                if isinstance(media, Animation):
                    await bot.send_animation(chat, media.file_id, text)
                elif isinstance(media, Document):
                    await bot.send_document(
                        chat, media.file_id, caption=text, force_document=True
                    )
                elif isinstance(media, Photo):
                    await bot.send_photo(chat, media.file_id, text)
                elif isinstance(media, Video):
                    await bot.send_video(chat, media.file_id, text)
                elif isinstance(media, Sticker):
                    await bot.send_sticker(chat, media.file_id)
                else:
                    await bot.send_message(chat, text)
                success.append(chat)
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except BaseException:
                failed.append(chat)

        await sent.edit_text(
            lang.alert_sent_text.format(
                success=len(success),
                failed=len(failed),
            ),
        )
