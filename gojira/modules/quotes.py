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
@Gojira.on_callback_query(filters.regex(r"^quote (\d+)?"))
@use_chat_language()
async def quote_message(bot: Gojira, union: Union[Message, CallbackQuery]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    lang = union._lang

    if is_callback:
        user_id = union.matches[0].group(1)
        if user_id is not None:
            user_id = int(user_id)

            if user_id != user.id:
                await union.answer(
                    lang.button_not_for_you,
                    show_alert=True,
                    cache_time=60,
                )
                return

    if not is_callback:
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

    button = [[("🔁", f"quote {user.id}")]]

    await (message if is_callback else sent).edit_text(text, reply_markup=ikb(button))
