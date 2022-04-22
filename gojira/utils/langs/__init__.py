"""Gojira langs utilities."""
# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from typing import List

from .core import Langs
from .load_langs import get_languages, load_languages

chat_languages = {}
user_languages = {}

__all__: List[str] = ["Langs", "get_languages", "load_languages"]
