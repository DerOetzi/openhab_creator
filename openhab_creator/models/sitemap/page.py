from __future__ import annotations
from typing import TYPE_CHECKING, Dict

from openhab_creator.models.sitemap.text import Text
from openhab_creator.models.sitemap.frame import Frame

if TYPE_CHECKING:
    from openhab_creator.models.sitemap.baseelement import BaseElement


class Page(Text):

    def __init__(self, **args):
        super().__init__(**args)
        self.__main: Frame = Frame()
        super().append(self.__main)

        self.__frames: Dict[str, Frame] = {}

    def frame(self, identifier: str, label: str) -> Frame:
        if identifier not in self.__frames:
            self.__frames[identifier] = Frame(label)
            super().append(self.__frames[identifier])

        return self.__frames[identifier]

    def append(self, element: BaseElement) -> None:
        self.__main.append(element)

    def dump(self) -> str:
        if len(self.__frames) == 0 and not self.__main.has_elements():
            return ''

        return super().dump()
