# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>

from typing import Union

import httpx
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"quote$"))
@Gojira.on_callback_query(filters.regex(r"^quote$"))
@use_chat_language()
async def quote_message(bot: Gojira, union: Union[Message, CallbackQuery]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    lang = union._lang

    if not is_callback:
        sent = await message.reply_text(lang.getting_quote)

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get("https://animechan.vercel.app/api/random")
        if response.status_code != 200:
            await sent.edit_text(lang.something_wrong)
            return
        data = response.json()
        await client.aclose()

    text = f"<code>❝{data['quote']}❞</code>\n\n"
    text += f"  ~ <b>{data['character']}</b> (<i>{data['anime']}</i>)"

    button = [[("🔁", "quote")]]

    await (message if is_callback else sent).edit_text(text, reply_markup=ikb(button))
