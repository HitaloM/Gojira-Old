# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>

import httpx
from pyrogram import filters
from pyrogram.types import Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"quote$"))
@use_chat_language()
async def quote_message(bot: Gojira, message: Message):
    lang = message._lang
    sent = await message.reply_text(lang.getting_quote)

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get("https://animechan.vercel.app/api/random")
        if response.status_code != 200:
            await sent.edit_text(lang.something_wrong)
            return
        data = response.json()
        await client.aclose()

    text = f"<code>{data['quote']}</code>\n\n"
    text += f"  ~ <b>{data['character']}</b> (<i>{data['anime']}</i>)"

    await sent.edit_text(text)
