from __future__ import annotations
from typing import List, TYPE_CHECKING

from openhab_creator.secretsregistry import SecretsRegistry

from openhab_creator.models.thing import Thing

if TYPE_CHECKING:
    from openhab_creator.models.equipment import Equipment


class Bridge(Thing):
    VALIDTYPES = [
        'deconz',
        'mqtt'
    ]

    _things: List[Equipment] = []
    _bridgetype: str
    _nameprefix: str

    def __init__(self, configuration: dict):
        name = configuration.get('name')
        super().__init__(name, configuration, Bridge.VALIDTYPES)

        self._bridgetype = configuration.get('bridgetype')
        self._nameprefix = configuration.get('nameprefix', '')

        self._initializeSecrets(configuration)
        self._initializeReplacements()

    def _getSecret(self, secretKey: str) -> str:
        return SecretsRegistry.secret(self._typed, self._id, secretKey)

    def _initializeReplacements(self) -> None:
        super()._initializeReplacements()
        self._replacements['bridgetype'] = self._bridgetype
        self._replacements['nameprefix'] = self._nameprefix

    def bridgetype(self) -> str:
        return self._bridgetype

    def nameprefix(self) -> str:
        return self._nameprefix

    def appendThing(self, thing: Equipment) -> None:
        self._things.append(thing)

    def things(self) -> List[Equipment]:
        return self._things
