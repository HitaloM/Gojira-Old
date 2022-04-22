# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import logging

import aiosqlite

from gojira.config import DATABASE_PATH

logger = logging.getLogger(__name__)


class Database(object):
    def __init__(self):
        self.conn: aiosqlite.Connection = None
        self.path: str = DATABASE_PATH
        self.is_connected: bool = False

    async def connect(self):
        # Open the connection
        conn = await aiosqlite.connect(self.path)

        # Define the tables
        await conn.executescript(
            """
        CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                language VARCHAR(2) NOT NULL DEFAULT \"en\",
                registration_time INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY,
                language VARCHAR(2) NOT NULL DEFAULT \"en\",
                registration_time INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY,
                user INTEGER NOT NULL,
                item INTEGER,
                type VARCHAR(7)
        );

        CREATE TABLE IF NOT EXISTS nhentai (
                id INTEGER PRIMARY KEY,
                artist TEXT,
                photo TEXT,
                title TEXT,
                pages TEXT,
                tags TEXT,
                url TEXT
        );
        """
        )

        # Enable VACUUM
        await conn.execute("VACUUM")

        # Enable WAL
        await conn.execute("PRAGMA journal_mode=WAL")

        # Update the database
        await conn.commit()

        conn.row_factory = aiosqlite.Row

        self.conn = conn
        self.is_connected: bool = True

        logger.info("The database has been connected.")

    async def close(self):
        # Close the connection
        await self.conn.close()

        self.is_connected: bool = False

        logger.info("The database was closed.")

    def get_conn(self) -> aiosqlite.Connection:
        if not self.is_connected:
            raise RuntimeError("The database is not connected.")

        return self.conn


database = Database()
