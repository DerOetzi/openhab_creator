from __future__ import annotations
from typing import Dict, Optional, Union, TYPE_CHECKING

from copy import deepcopy

from openhab_creator.models import ConfigurationType, BaseObject

SecretsType = Dict[str, str]
ReplacementsType = Dict[str, str]
PropertyType = Union[str, bool, int]
PropertiesType = Dict[str, PropertyType]


class BaseThing(BaseObject):
    def __init__(self, name: str, configuration: ConfigurationType, id: Optional(str) = None):
        super().__init__(name, configuration, id)
        self._secrets: SecretsType = {}
        self._replacements: ReplacementsType = {}
        self._properties: PropertiesType = configuration['properties'] if 'properties' in configuration else {
        }

    def _cast(self, obj: BaseThing) -> None:
        super()._cast(obj)
        self._secrets: SecretsType = deepcopy(obj._secrets)
        self._replacements: ReplacementsType = deepcopy(obj._replacements)
        self._properties: PropertiesType = deepcopy(obj._properties)

    def _initialize_secrets(self, configuration: ConfigurationType) -> None:
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

    def replacements(self) -> ReplacementsType:
        return self._replacements

    def properties(self) -> PropertiesType:
        return self._properties
