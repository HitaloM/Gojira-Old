# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import glob
import re
from typing import Dict

import yaml

from gojira.utils.langs import Langs

strings: Dict = {}


def get_languages(only_codes: bool = False):
    if only_codes:
        return strings.keys()

    if len(strings.keys()) < 1:
        load_languages()

    return Langs(**strings)


def load_languages() -> None:
    for string_file in glob.glob("gojira/locales/*.yml"):
        language_code = re.match(r"gojira/locales/(.+)\.yml$", string_file)[1]
        strings[language_code] = yaml.safe_load(open(string_file, "r"))
