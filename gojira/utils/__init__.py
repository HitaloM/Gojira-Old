"""Gojira utilities."""
# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
import os
import platform
import sys

from . import filters, modules

__all__ = ["filters", "modules"]


def is_windows() -> bool:
    return bool(
        platform.system().lower() == "windows"
        or os.name == "nt"
        or sys.platform.startswith("win")
    )


async def shell_exec(code: str, treat=True) -> str:
    process = await asyncio.create_subprocess_shell(
        code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )

    stdout = (await process.communicate())[0]
    if treat:
        stdout = stdout.decode().strip()
    return stdout, process
