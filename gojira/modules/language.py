# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from contextlib import suppress
from typing import List, Tuple, Union

from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.helpers import array_chunk, bki, ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.database.language import update_chat_language, update_user_language
from gojira.utils.langs.decorators import (
    chat_languages,
    use_chat_language,
    user_languages,
)
from gojira.utils.langs.methods import get_user_lang


@Gojira.on_message(filters.cmd(r"language$"))
@Gojira.on_callback_query(filters.regex(r"^language$"))
@use_chat_language()
async def language(c: Gojira, m: Union[Message, CallbackQuery]):
    lang = m._lang
    if isinstance(m, Message):
        chat = m.chat
        user = m.from_user

        if chat.type in ["group", "supergroup"]:
            member = await c.get_chat_member(chat.id, user.id)
            if member.status not in ["administrator", "creator"]:
                await m.reply_text(
                    lang.get_language(await get_user_lang(user.id)).not_admin
                )
                return

    buttons: List[Tuple] = []
    for code, obj in lang.strings.items():
        text, data = (
            (f"✅ {obj['LANGUAGE_NAME']}", "noop")
            if obj["LANGUAGE_CODE"] == lang.LANGUAGE_CODE
            else (obj["LANGUAGE_NAME"], f"language set {obj['LANGUAGE_CODE']}")
        )
        buttons.append((text, data))

    keyboard = array_chunk(buttons, 2)

    if isinstance(m, CallbackQuery):
        keyboard.append([(lang.back_button, "start")])

    await (m.message.edit_text if isinstance(m, CallbackQuery) else m.reply_text)(
        lang.language_text.format(lang_name=lang.LANGUAGE_NAME),
        reply_markup=ikb(keyboard),
    )


@Gojira.on_callback_query(filters.regex(r"^language set (?P<code>\w+)"))
@use_chat_language()
async def language_set(c: Gojira, q: CallbackQuery):
    message = q.message
    chat = message.chat
    user = q.from_user
    lang = q._lang

    if chat.type in ["group", "supergroup"]:
        member = await c.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"]:
            await q.answer(
                lang.get_language(await get_user_lang(user.id)).not_admin,
                show_alert=True,
                cache_time=60,
            )
            return

    language_code = q.matches[0]["code"]

    if chat.type == "private":
        await update_user_language(user.id, language_code)
        user_languages[user.id] = language_code
    else:
        await update_chat_language(chat.id, language_code)
        chat_languages[chat.id] = language_code

    nlang = lang.get_language(language_code)
    text = nlang.language_changed_alert.format(lang_name=nlang.LANGUAGE_NAME)

    for line in bki(message.reply_markup):
        for button in line:
            if button[0] == lang.back_button:
                await q.answer(text, show_alert=True)
                with suppress(MessageNotModified):
                    await language(c, q)
                return

    await q.edit_message_text(text)
