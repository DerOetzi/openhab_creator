from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING

from openhab_creator.exception import ConfigurationException
from openhab_creator.secretsregistry import SecretsRegistry

from openhab_creator.models import ConfigurationType

from openhab_creator.models.thing import BaseThing

if TYPE_CHECKING:
    from openhab_creator.models.equipment import Equipment


class Bridge(BaseThing):
    VALIDTYPES = [
        'deconz',
        'mqtt'
    ]

    def __init__(self, configuration: ConfigurationType):
        name = configuration.get('name')
        super().__init__(name, configuration)

        self._bridgetype: str = configuration.get('bridgetype')
        self._nameprefix: str = configuration.get('nameprefix', '')

        self._initialize_secrets(configuration)
        self._initialize_replacements()

        self._things: List[Equipment] = []

    def _get_secret(self, secret_key: str) -> str:
        return SecretsRegistry.secret(self._typed, self._id, secret_key)

    def _default_type(self) -> str:
        raise ConfigurationException(
            'Bridge always need a type defined in configuration')

    def _is_valid_type(self, typed: str) -> bool:
        return typed in Bridge.VALIDTYPES

    def _initialize_replacements(self) -> None:
        super()._initialize_replacements()
        self._replacements['bridgetype'] = self._bridgetype
        self._replacements['nameprefix'] = self._nameprefix

    def bridgetype(self) -> str:
        return self._bridgetype

    def nameprefix(self) -> str:
        return self._nameprefix

    def things(self) -> List[Equipment]:
        return self._things

    def append_thing(self, thing: Equipment) -> None:
        self._things.append(thing)
