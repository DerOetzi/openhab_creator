from __future__ import annotations
from abc import ABC
from typing import Optional, Final

from openhab_creator.output.formatter import Formatter


class BaseObject(ABC):
    def __init__(self,
                 name: str,
                 identifier: Optional[str] = None):
        self.__NAME: Final[str] = name
        self.identifier = name if identifier is None else identifier

    @property
    def name(self) -> str:
        return self.__NAME

    @property
    def identifier(self) -> str:
        return self.__IDENTIFIER

    @identifier.setter
    def identifier(self, identifier: str):
        identifier = Formatter.format_id(identifier)
        self.__IDENTIFIER: Final[str] = Formatter.ucfirst(identifier)

    @property
    def category(self) -> str:
        return self.__class__.__name__.lower()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self.name} ({self.identifier}, {self.__class__.__name__})'
