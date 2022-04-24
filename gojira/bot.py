# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import datetime
import logging

import aiocron
import sentry_sdk
from pyrogram import Client, __version__
from pyrogram.errors import BadRequest
from pyrogram.raw.all import layer
from pyrogram.types import User

import gojira
from gojira.config import API_HASH, API_ID, BOT_TOKEN, CHATS, SENTRY_KEY, SUDO_USERS
from gojira.utils import backup, modules, shell_exec
from gojira.utils.langs import get_languages, load_languages

logger = logging.getLogger(__name__)


class Gojira(Client):
    def __init__(self):
        name = self.__class__.__name__.lower()

        super().__init__(
            session_name=name,
            app_version=f"Gojira v{gojira.__version__}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            parse_mode="html",
            workers=24,
            workdir="gojira",
            sleep_threshold=180,
        )

        self.sudos = SUDO_USERS

        self.start_datetime = datetime.datetime.now().replace(
            tzinfo=datetime.timezone.utc
        )

    async def start(self):
        await super().start()

        # Load the languages
        load_languages()
        languages = len(get_languages(only_codes=True))
        logger.info("%s languages was loaded.", languages)

        # Save version info
        self.version_code = int((await shell_exec("git rev-list --count HEAD"))[0])
        self.version = str((await shell_exec("git rev-parse --short HEAD"))[0])

        if not SENTRY_KEY or SENTRY_KEY == "":
            logger.warning("No sentry.io key found! Service not initialized.")
        else:
            logger.info("Starting sentry.io service.")
            sentry_sdk.init(SENTRY_KEY, traces_sample_rate=1.0)

        self.me = await self.get_me()
        logger.info(
            "Gojira running with Pyrogram v%s (Layer %s) started on @%s. Hi!",
            __version__,
            layer,
            self.me.username,
        )

        modules.load(self)

        if CHATS["backup"]:
            aiocron.crontab("0 * * * *", func=backup.save, args=(self,), start=True)
        else:
            logger.info("Backups disabled.")

        try:
            for sudo in self.sudos:
                await self.send_message(
                    chat_id=sudo,
                    text=(
                        f"<b>Gojira</b> <a href='https://github.com/HitaloSama/Gojira/commit/{self.version}'>{self.version}</a> (<code>{self.version_code}</code>) started!"
                        f"\n<b>Pyrogram</b> <code>v{__version__}</code> (Layer {layer})"
                    ),
                    disable_web_page_preview=True,
                )
        except BadRequest:
            logger.error("Error while sending the startup message.", exc_info=True)

    async def stop(self):
        await super().stop()
        logger.warning("Gojira stopped. Bye!")

    def is_sudo(self, user: User) -> bool:
        return user.id in self.sudos
