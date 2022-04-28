# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2020 Cezar H. <https://github.com/usernein>

import html
from typing import Dict, List


class LangsFormatMap(dict):
    def __getitem__(self, key):
        if key in self:
            if type(self.get(key)) is str:
                return html.escape(self.get(key))
        return str("{" + key + "}")


class LangString(str):
    def __call__(self, **kwargs):
        mapping = LangsFormatMap(**kwargs)
        mapping.string = self.key
        mapping.code = self.code
        formatted = self.format_map(mapping)
        return formatted


class Langs:
    strings: Dict = {}
    available: List = []
    code: str = "en"

    def __init__(self, strings: Dict = None, **kwargs):
        if strings is None:
            strings = {}
        self.strings = strings

        if not kwargs and not strings:
            raise ValueError(
                "Pass the language codes and their objects (dictionaries containing the strings) as keyword arguments (language=dict)"
            )

        for language_code, strings_object in kwargs.items():
            self.strings[language_code] = strings_object
            self.strings[language_code].update({"LANGUAGE_CODE": language_code})

        self.available = list(self.strings.keys())
        self.code = "en" if "en" in self.available else self.available[0]

    def __getattr__(self, key):
        try:
            result = self.strings[self.code][key]
        except KeyError:
            result = self.strings["en"][key]
        obj = LangString(result)
        obj.key = key
        obj.code = self.code
        return obj

    def get_language(self, language_code: str):
        lang_copy = Langs(strings=self.strings)
        lang_copy.code = language_code
        return lang_copy
