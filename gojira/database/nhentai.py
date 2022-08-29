# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>

from typing import Dict, Optional

from .core import database

conn = database.get_conn()


async def get_nhentai_all() -> Dict:
    cursor = await conn.execute("SELECT * FROM nhentai")
    rows = await cursor.fetchall()
    await cursor.close()
    return rows


async def get_nhentai_by_id(id: int) -> Optional[Dict]:
    cursor = await conn.execute("SELECT * FROM nhentai WHERE id = ?", (id,))
    row = await cursor.fetchone()
    await cursor.close()
    return row


async def create_nhentai(
    id: int,
    title: str,
    artist: str,
    tags: str,
    pages: int,
    photo: str,
    url: str,
) -> None:
    await conn.execute(
        "INSERT INTO nhentai (id, title, artist, tags, pages, photo, url) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (id, title, artist, tags, pages, photo, url),
    )
    if conn.total_changes <= 0:
        raise AssertionError
    await conn.commit()
