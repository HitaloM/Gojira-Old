# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>

from typing import Callable, Dict


class Studio:
    """Studio object."""

    def __init__(
        self,
        *,
        id: int,
        name: str,
        url: str,
        favorites: int,
        is_animation_studio: bool,
    ):
        self.id = id
        self.name = name
        self.is_animation_studio = is_animation_studio
        self.url = url
        self.favorites = favorites

    def raw(self) -> Dict:
        return self.__dict__

    def __repr__(self) -> Callable:
        return self.__str__()  # type: ignore

    def __str__(self) -> str:
        return str(self.raw())
