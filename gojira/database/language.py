# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from .core import database

conn = database.get_conn()


async def update_chat_language(id: int, language_code: str):
    await conn.execute(
        "UPDATE chats SET language = ? WHERE id = ?", (language_code, id)
    )
    if conn.total_changes <= 0:
        raise AssertionError
    await conn.commit()


async def update_user_language(id: int, language_code: str):
    await conn.execute(
        "UPDATE users SET language = ? WHERE id = ?", (language_code, id)
    )
    if conn.total_changes <= 0:
        raise AssertionError
    await conn.commit()
