from __future__ import annotations
from typing import Dict, List

from openhab_creator.models.baseobject import BaseObject


class BaseThing(BaseObject):
    _secrets: Dict[str, str]
    _replacements: Dict[str, str]
    _properties: Dict[str, str]

    def __init__(self, name: str, configuration: dict, id: str = None):
        super().__init__(name, configuration, id)
        self._secrets = {}
        self._replacements = {}
        self._properties = configuration['properties'] if 'properties' in configuration else {
        }

    def _cast(self, obj: BaseThing) -> None:
        super()._cast(obj)
        self._secrets = obj._secrets
        self._replacements = obj._replacements
        self._properties = obj._properties

    def _initialize_secrets(self, configuration: dict) -> None:
        if 'secrets' in configuration:
            for secret_key in configuration['secrets']:
                self._secrets[secret_key] = self._get_secret(secret_key)

    def _get_secret(self, secret_key: str) -> str:
        raise NotImplementedError("Must override _getSecret")

    def _initialize_replacements(self) -> None:
        self._replacements = {
            "name": self._name,
            "type": self._typed,
            "id": self._id
        }

        for key, value in self._secrets.items():
            self._replacements[key] = value

    def replacements(self) -> Dict[str, str]:
        return self._replacements

    def properties(self) -> Dict[str, str]:
        return self._properties
