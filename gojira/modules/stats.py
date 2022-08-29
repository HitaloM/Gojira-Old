# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import datetime
import os
import platform
import shutil

import humanize
import psutil
from pyrogram import filters
from pyrogram.types import Message

from gojira.bot import Gojira
from gojira.config import DATABASE_PATH
from gojira.database import database
from gojira.database.chats import filter_chats_by_language
from gojira.database.users import filter_users_by_language
from gojira.utils.langs.decorators import use_chat_language

conn = database.get_conn()


@Gojira.on_message(filters.cmd(r"stats$") & filters.sudo)
@use_chat_language()
async def stats_view(bot: Gojira, message: Message):
    lang = message._lang
    text = "\n<b>Database</b>"
    text += f"\n    <b>Size</b>: <code>{humanize.naturalsize(os.stat(DATABASE_PATH).st_size, binary=True)}</code>"
    disk = shutil.disk_usage("/")
    text += (
        f"\n    <b>Free</b>: <code>{humanize.naturalsize(disk[2], binary=True)}</code>"
    )
    text += "\n<b>Chats</b>"
    users_count = await conn.execute("select count() from users")
    users_count = await users_count.fetchone()
    text += f"\n    <b>Users</b>: <code>{users_count[0]}</code>"
    for language in lang.strings.keys():
        users = await filter_users_by_language(language=language)
        text += f"\n        <b>{language.upper()}</b>: <code>{len(users)}</code>"
    groups_count = await conn.execute("select count() from chats")
    groups_count = await groups_count.fetchone()
    text += f"\n    <b>Groups</b>: <code>{groups_count[0]}</code>"
    for language in lang.strings.keys():
        groups = await filter_chats_by_language(language=language)
        text += f"\n        <b>{language.upper()}</b>: <code>{len(groups)}</code>"
    text += "\n<b>System</b>"
    uname = platform.uname()
    text += f"\n    <b>OS</b>: <code>{uname.system}</code>"
    text += f"\n    <b>Node</b>: <code>{uname.node}</code>"
    text += f"\n    <b>Kernel</b>: <code>{uname.release}</code>"
    text += f"\n    <b>Architecture</b>: <code>{uname.machine}</code>"
    memory = psutil.virtual_memory()
    text += f"\n    <b>Memory</b>: <code>{humanize.naturalsize(memory.used, binary=True)}/{humanize.naturalsize(memory.total, binary=True)}</code>"
    now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    date = now - bot.start_datetime
    text += f"\n    <b>UPTime</b>: <code>{humanize.precisedelta(date)}</code>"

    await message.reply_text(text)
