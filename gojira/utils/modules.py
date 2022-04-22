# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import glob
import importlib
import logging
from types import ModuleType
from typing import List

logger = logging.getLogger(__name__)


modules: List[ModuleType] = []


def load(bot):
    files = glob.glob("gojira/modules/**/*.py", recursive=True)
    main_dir = sorted(
        [*filter(lambda file: len(file.split("/")) == 3, files)],
        key=lambda file: file.split("/")[2],
    )
    sub_dirs = sorted(
        [*filter(lambda file: len(file.split("/")) >= 4, files)],
        key=lambda file: file.split("/")[3],
    )
    files = main_dir + sub_dirs

    for file_name in files:
        try:
            module = importlib.import_module(
                file_name.replace("/", ".").replace(".py", "")
            )
            modules.append(module)
        except BaseException:
            logger.critical("Failed to import the module: %s", file_name, exc_info=True)
            continue

        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda function: hasattr(function, "handlers"), functions)]

        for function in functions:
            for handler in function.handlers:
                bot.add_handler(*handler)

    logger.info(
        "%s module%s imported successfully!",
        len(modules),
        "s" if len(modules) != 1 else "",
    )


def reload(bot):
    for index, module in enumerate(modules):
        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda function: hasattr(function, "handlers"), functions)]

        for function in functions:
            for handler in function.handlers:
                bot.remove_handler(*handler)

        module = importlib.reload(module)
        modules[index] = module

        functions = [*filter(callable, module.__dict__.values())]
        functions = [*filter(lambda function: hasattr(function, "handlers"), functions)]

        for function in functions:
            for handler in function.handlers:
                bot.add_handler(*handler)

    logger.info(
        "%s module%s reloaded successfully!",
        len(modules),
        "s" if len(modules) != 1 else "",
    )
