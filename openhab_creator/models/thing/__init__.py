from __future__ import annotations
from typing import Dict, List, Optional

from copy import deepcopy

from openhab_creator.exception import BuildException
from openhab_creator.models import BaseObject


class BaseThing(BaseObject):
    def __init__(self, typed: str, name: str, identifier: Optional[str] = None,
                 secrets: Optional[List[str]] = [],
                 properties: Optional[Dict] = {},
                 points: Optional[Dict[str, Dict[str, str]]] = {}):

        super().__init__(typed, name, identifier)

        self._replacements: Dict[str, str] = {}

        self.__secrets_config: List[str] = secrets
        self.__secrets: Dict[str, str] = {}
        self.__properties: Dict = properties
        self.__points: Dict[str, Dict] = points

    def _init_secrets(self):
        for secret_key in self.__secrets_config:
            self.__secrets[secret_key] = self._get_secret(secret_key)

    def _get_secret(self, secret_key: str) -> str:
        raise NotImplementedError("Must override _getSecret")

    def _init_replacements(self) -> None:
        self._replacements = {
            "name": self._name,
            "type": self._typed,
            "identifier": self._identifier
        }

        for key, value in self.__secrets.items():
            self._replacements[key] = value

    def replacements(self) -> Dict[str, str]:
        return self._replacements

    def properties(self) -> Dict:
        return self.__properties

    def points(self, point_key: str) -> Dict[str, str]:
        if point_key in self.__points:
            return self.__points[point_key]

        return {}

    def point(self, point_key: str, point: str) -> str:
        if point_key not in self.__points:
            raise BuildException(f'Unknown pointtype {point_key}')

        if point not in self.__points[point_key]:
            raise BuildException(f'Unknown point {point} in {point_key}')

        return self.__points[point_key][point]
