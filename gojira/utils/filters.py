# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import re
from typing import Callable, Union

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from gojira.config import PREFIXES


def filter_cmd(pattern: str, flags: int = 0) -> Callable:
    pattern = r"^" + f"[{re.escape(''.join(PREFIXES))}]" + pattern
    if not pattern.endswith(("$", " ")):
        pattern += r"(?:\s|$)"

    async def func(flt, bot, message: Message):
        value = message.text or message.caption

        if bool(value):
            command = value.split()[0]
            if "@" in command:
                b = command.split("@")[1]
                if b.lower() == bot.me.username.lower():
                    value = (
                        command.split("@")[0]
                        + (" " if len(value.split()) > 1 else "")
                        + " ".join(value.split()[1:])
                    )

            message.matches = list(flt.p.finditer(value)) or None

        return bool(message.matches)

    return filters.create(
        func,
        "CommandHandler",
        p=re.compile(pattern, flags),
    )


async def filter_sudo(_, bot, union: Union[CallbackQuery, Message]) -> Callable:
    user = union.from_user
    if not user:
        return False
    return bot.is_sudo(user)


async def filter_administrator(_, bot, union: Union[CallbackQuery, Message]) -> bool:
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    chat = message.chat
    user = union.from_user

    member = await bot.get_chat_member(chat.id, user.id)
    return member.status in ["administrator", "creator"]


filters.cmd = filter_cmd
filters.sudo = filters.create(filter_sudo, "FilterSudo")
filters.administrator = filters.create(filter_administrator, "FilterAdministrator")
