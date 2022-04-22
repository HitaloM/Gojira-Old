# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>

from typing import Dict, Optional

from .core import database

conn = database.get_conn()


async def get_user_favorites(user: int, item: int, type: str) -> Optional[Dict]:
    cursor = await conn.execute(
        "SELECT * FROM favorites WHERE user = ? AND item = ? AND type = ?",
        (
            user,
            item,
            type,
        ),
    )
    row = await cursor.fetchone()
    await cursor.close()
    return row


async def create_user_favorite(user: int, item: int, type: str) -> None:
    await conn.execute(
        "INSERT INTO favorites (user, item, type) VALUES (?, ?, ?)",
        (user, item, type),
    )
    if conn.total_changes <= 0:
        raise AssertionError
    await conn.commit()


async def delete_user_favorite(user: int, item: int, type: str) -> None:
    await conn.execute(
        "DELETE FROM favorites WHERE user = ? AND item = ? AND type = ?",
        (user, item, type),
    )
    if conn.total_changes <= 0:
        raise AssertionError
    await conn.commit()


async def filter_user_favorites(user: int, type: str) -> Dict:
    cursor = await conn.execute(
        "SELECT * FROM favorites WHERE user = ? AND type = ?",
        (user, type),
    )
    rows = await cursor.fetchall()
    await cursor.close()
    return rows
