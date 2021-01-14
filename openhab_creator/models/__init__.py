from __future__ import annotations
from typing import Dict, Optional

from openhab_creator.exception import ConfigurationException

from openhab_creator.output.formatter import Formatter


class BaseObject(object):
    def __init__(self, typed: str, name: str, identifier: Optional[str] = None):
        self._name: str = name
        self._identifier: str = identifier
        self._typed: str = typed

        if self._identifier is None:
            self._identifier = Formatter.format_id(self._name)

        self._identifier = Formatter.ucfirst(self._identifier)

    def identifier(self) -> str:
        return self._identifier

    def name(self) -> str:
        return self._name

    def typed(self) -> str:
        return self._typed

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self._name} ({self._identifier}, {self._typed})'
