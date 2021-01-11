from __future__ import annotations
from typing import Dict, List, Optional, Union

from openhab_creator.exception import ConfigurationException

from openhab_creator.output.formatter import Formatter

ConfigurationType = Dict[str, Union[str, Dict, List]]


class BaseObject(object):
    def __init__(self, name: str, configuration: ConfigurationType, id: Optional(str) = None):
        self._id: str = id

        if self._id is None:
            self._id = configuration.get('id', None)
            if self._id is None:
                self._id = Formatter.format_id(name)
        else:
            self._id = id

        self._id = Formatter.ucfirst(self._id)

        self._name: str = name

        self._typed: str = configuration.get('type', None)
        if self._typed is None:
            self._typed = self._default_type()
        else:
            self._typed = self._typed.lower()
            if not self._is_valid_type(self._typed):
                raise ConfigurationException(
                    f'Invalid type {self._typed} for {name}')

        self._icon: str = configuration.get('icon', None)
        if self._icon is None:
            self._icon = self._typed

    def _cast(self, obj: BaseObject) -> None:
        self._id: str = str(obj._id)
        self._name: str = str(obj._name)
        self._typed: str = str(obj._typed)
        self._icon: str = str(obj._icon)

    def _default_type(self) -> str:
        raise NotImplementedError("Must override _default_type")

    def _is_valid_type(self, typed: str) -> bool:
        raise NotImplementedError('Must override _is_valid_type')

    def id(self) -> str:
        return self._id

    def name(self) -> str:
        return self._name

    def typed(self) -> str:
        return self._typed

    def icon(self) -> str:
        return self._icon

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self._name} ({self._id}, {self._typed})'
