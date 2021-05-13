from __future__ import annotations
from abc import ABC
from typing import Optional

from openhab_creator.output.formatter import Formatter


class BaseObject(ABC):
    def __init__(self,
                 name: str,
                 identifier: Optional[str] = None):
        self.name: str = name
        self.identifier = identifier or name

    @property
    def identifier(self) -> str:
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: str) -> BaseObject:
        identifier = Formatter.format_id(identifier)
        self._identifier: str = Formatter.ucfirst(identifier)
        return self

    @property
    def semantic(self) -> str:
        return self.__class__.__name__

    @property
    def category(self) -> str:
        return self.semantic.lower()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self.name} ({self.identifier}, {self.category})'
