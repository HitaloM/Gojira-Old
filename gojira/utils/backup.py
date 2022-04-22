# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import datetime
import logging

from pyrogram import Client

from gojira.config import CHATS, DATABASE_PATH

logger = logging.getLogger(__name__)


async def save(bot: Client):
    date = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    logger.warning("Saving the database in Telegram...")

    try:
        if await bot.send_document(
            CHATS["backup"],
            DATABASE_PATH,
            caption=f"<b>Database BACKUP</b>\n\n<b>Date</b>: <code>{date}</code>",
        ):
            logger.warning("Database saved in Telegram successfully!")
        else:
            logger.warning("It was not possible to save the database in Telegram.")
    except BaseException:
        logger.error("Error saving the database in Telegram.", exc_info=True)
