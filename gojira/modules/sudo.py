# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
import datetime
import io
import os
import sys
import traceback
from signal import SIGINT
from typing import Dict

import meval
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.utils import modules


@Gojira.on_message(filters.cmd(r"up(grad|dat)e$") & filters.sudo)
async def upgrade_message(bot: Gojira, message: Message):
    sent = await message.reply_text("Checking for updates...")

    await (await asyncio.create_subprocess_shell("git fetch origin")).communicate()
    proc = await asyncio.create_subprocess_shell(
        "git log HEAD..origin/main",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout = (await proc.communicate())[0].decode()

    if proc.returncode == 0:
        if len(stdout) > 0:
            changelog = "<b>Changelog</b>:\n"
            commits = parse_commits(stdout)
            for c_hash, commit in commits.items():
                changelog += f"  - [<code>{c_hash[:7]}</code>] {commit['title']}\n"
            changelog += f"\n<b>New commits count</b>: <code>{len(commits)}</code>."

            keyboard = [[("🆕 Upgrade", "upgrade")]]
            await sent.edit_text(changelog, reply_markup=ikb(keyboard))
        else:
            await sent.edit_text("There is nothing to update.")
    else:
        error = ""
        lines = stdout.split("\n")
        for line in lines:
            error += f"<code>{line}</code>\n"
        await sent.edit_text(
            f"Update failed (process exited with {proc.returncode}):\n{error}"
        )


def parse_commits(log: str) -> Dict:
    commits: Dict = {}
    last_commit = ""
    lines = log.split("\n")
    for line in lines:
        if line.startswith("commit"):
            last_commit = line.split()[1]
            commits[last_commit] = {}
        if len(line) > 0:
            if line.startswith("    "):
                if "title" in commits[last_commit].keys():
                    commits[last_commit]["message"] = line[4:]
                else:
                    commits[last_commit]["title"] = line[4:]
            else:
                if ":" in line:
                    key, value = line.split(": ")
                    commits[last_commit][key] = value
    return commits


@Gojira.on_callback_query(filters.regex(r"^upgrade$") & filters.sudo)
async def upgrade_callback(bot: Gojira, callback: CallbackQuery):
    await callback.edit_message_reply_markup({})
    sent = await callback.message.reply_text("Upgrading...")

    proc = await asyncio.create_subprocess_shell(
        "git reset --hard origin/main",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout = (await proc.communicate())[0].decode()

    if proc.returncode == 0:
        await sent.edit_text("Restarting...")
        args = [sys.executable, "-m", "gojira"]
        os.execv(sys.executable, args)
    else:
        error = ""
        lines = stdout.split("\n")
        for line in lines:
            error += f"<code>{line}</code>\n"
        await sent.edit_text(
            f"Update failed (process exited with {proc.returncode}):\n{error}"
        )


@Gojira.on_message(filters.cmd(r"re(boot|start)") & filters.sudo)
async def reboot_message(bot: Gojira, message: Message):
    await message.reply_text("Restarting...")
    args = [sys.executable, "-m", "gojira"]
    os.execv(sys.executable, args)


@Gojira.on_message(filters.cmd(r"shutdown") & filters.sudo)
async def shutdown_message(bot: Gojira, message: Message):
    await message.reply_text("Turning off...")
    os.kill(os.getpid(), SIGINT)


@Gojira.on_message(filters.cmd("(sh(eel)?|term(inal)?) ") & filters.sudo)
async def terminal_message(bot: Gojira, message: Message):
    command = message.text.split()[0]
    code = message.text[len(command) + 1 :]
    sent = await message.reply_text("Running...")

    proc = await asyncio.create_subprocess_shell(
        code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout = (await proc.communicate())[0]

    lines = stdout.decode().splitlines()
    output = "".join(f"<code>{line}</code>\n" for line in lines)
    output_message = f"<b>Input\n&gt;</b> <code>{code}</code>\n\n"
    if len(output) > 0:
        if len(output) > (4096 - len(output_message)):
            document = io.BytesIO(
                (output.replace("<code>", "").replace("</code>", "")).encode()
            )
            document.name = "output.txt"
            await bot.send_document(chat_id=message.chat.id, document=document)
        else:
            output_message += f"<b>Output\n&gt;</b> {output}"

    await sent.edit_text(output_message)


@Gojira.on_message(filters.cmd("ev(al)? ") & filters.sudo)
async def eval_message(bot: Gojira, message: Message):
    command = message.text.split()[0]
    eval_code = message.text[len(command) + 1 :]
    sent = await message.reply_text("Running...")

    try:
        stdout = await meval.meval(eval_code, globals(), **locals())
    except BaseException:
        error = traceback.format_exc()
        await sent.edit_text(
            f"An error occurred while running the code:\n<code>{error}</code>"
        )
        return

    output_message = f"<b>Input\n&gt;</b> <code>{eval_code}</code>\n\n"

    if stdout is not None:
        lines = str(stdout).splitlines()
        output = "".join(f"<code>{line}</code>\n" for line in lines)

        if len(output) > 0:
            if len(output) > (4096 - len(output_message)):
                document = io.BytesIO(
                    (output.replace("<code>", "").replace("</code>", "")).encode()
                )
                document.name = "output.txt"
                await bot.send_document(chat_id=message.chat.id, document=document)
            else:
                output_message += f"<b>Output\n&gt;</b> {output}"

    await sent.edit_text(output_message)


@Gojira.on_message(filters.cmd("ex(ec(ute)?)? ") & filters.sudo)
async def execute_message(bot: Gojira, message: Message):
    command = message.text.split()[0]
    code = message.text[len(command) + 1 :]
    sent = await message.reply_text("Running...")

    function = "async def _aexec_(bot: Gojira, message: Message):"
    for line in code.splitlines():
        function += f"\n    {line}"
    exec(function)

    try:
        stdout = await locals()["_aexec_"](bot, message)
    except BaseException:
        error = traceback.format_exc()
        await sent.edit_text(
            f"An error occurred while running the code:\n<code>{error}</code>"
        )
        return

    output_message = f"<b>Input\n&gt;</b> <code>{code}</code>\n\n"

    if stdout is not None:
        lines = str(stdout).splitlines()
        output = "".join(f"<code>{line}</code>\n" for line in lines)

        if len(output) > 0:
            if len(output) > (4096 - len(output_message)):
                document = io.BytesIO(
                    (output.replace("<code>", "").replace("</code>", "")).encode()
                )
                document.name = "output.txt"
                await bot.send_document(chat_id=message.chat.id, document=document)
            else:
                output_message += f"<b>Output\n&gt;</b> {output}"

    await sent.edit_text(output_message)


@Gojira.on_message(filters.cmd(r"reload$") & filters.sudo)
async def reload_message(bot: Gojira, message: Message):
    sent = await message.reply_text("Reloading modules...")
    first = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    modules.reload(bot)
    second = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    await sent.edit_text(
        f"Modules reloaded in <code>{(second - first).microseconds / 1000}ms</code>."
    )


@Gojira.on_message(filters.cmd(r"ping$") & filters.sudo)
async def ping_message(bot: Gojira, message: Message):
    start = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    sent = await message.reply_text("Pong!")
    end = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    await sent.edit_text(f"<code>{(end - start).microseconds / 1000}ms</code>")
