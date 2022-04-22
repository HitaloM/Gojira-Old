# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
import logging

from pyrogram.session import Session

from gojira.bot import Gojira, logger
from gojira.database import database
from gojira.utils import is_windows

# Custom logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s.%(funcName)s | %(levelname)s | %(message)s",
    datefmt="[%X]",
)

# To avoid some annoying log
logging.getLogger("pyrogram.syncer").setLevel(logging.WARNING)
logging.getLogger("pyrogram.client").setLevel(logging.WARNING)

# Use uvloop to improve speed if available
try:
    import uvloop

    uvloop.install()
except ImportError:
    if not is_windows():
        logger.warning("uvloop is not installed and therefore will be disabled.")

# Disable ugly pyrogram notice print
Session.notice_displayed = True


if __name__ == "__main__":
    # open new asyncio event loop
    event_policy = asyncio.get_event_loop_policy()
    event_loop = event_policy.new_event_loop()
    try:
        # start the bot
        event_loop.run_until_complete(database.connect())
        Gojira().run()
    except KeyboardInterrupt:
        # exit gracefully
        logger.warning("Forced stop... Bye!")
    finally:
        # close Database if open
        if database.is_connected:
            event_loop.run_until_complete(database.close())
        # close asyncio event loop
        event_loop.close()
