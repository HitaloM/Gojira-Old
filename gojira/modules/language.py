# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from contextlib import suppress
from typing import List, Tuple, Union

from pyrogram import filters
from pyrogram.enums import ChatType
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
async def language(bot: Gojira, union: Union[Message, CallbackQuery]):
    lang = union._lang
    if isinstance(union, Message):
        chat = union.chat

        if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            if not await filters.admin(bot, union):
                await union.reply_text(lang.not_admin)
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

    if isinstance(union, CallbackQuery):
        keyboard.append([(lang.back_button, "start")])

    await (
        union.message.edit_text
        if isinstance(union, CallbackQuery)
        else union.reply_text
    )(
        lang.language_text.format(lang_name=lang.LANGUAGE_NAME),
        reply_markup=ikb(keyboard),
    )


@Gojira.on_callback_query(filters.regex(r"^language set (?P<code>\w+)"))
@use_chat_language()
async def language_set(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    chat = message.chat
    user = callback.from_user
    lang = callback._lang

    if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        if not await filters.admin(bot, callback):
            await callback.answer(
                lang.get_language(await get_user_lang(user.id)).not_admin,
                show_alert=True,
                cache_time=60,
            )
            return

    language_code = callback.matches[0]["code"]

    if chat.type == ChatType.PRIVATE:
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
                await callback.answer(text, show_alert=True)
                with suppress(MessageNotModified):
                    await language(bot, callback)
                return

    await callback.edit_message_text(text)
