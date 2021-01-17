from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from openhab_creator.exception import ConfigurationException
from openhab_creator.models.thing.basething import BaseThing
from openhab_creator.models.secretsregistry import SecretsRegistry

if TYPE_CHECKING:
    from openhab_creator.models.thing.equipment.equipment import Equipment


class Bridge(BaseThing):
    def __init__(self, typed: str, name: str,
                 config: Dict[str, Union[str, bool]],
                 identifier: Optional[str] = None,
                 secrets: Optional[List[str]] = [],
                 properties: Optional[Dict[str, Dict]] = {},
                 points: Optional[str, Dict[str, str]] = {}):

        super().__init__(typed, name, identifier, secrets, properties, points)

        self._bridgetype: str = config.get('bridgetype')
        self._nameprefix: str = config.get('nameprefix', '')

        self._things: List[Equipment] = []

        self._init_secrets()
        self._init_replacements()

    def _get_secret(self, secret_key: str) -> str:
        return SecretsRegistry.secret(self._typed, self._identifier, secret_key)

    def _init_replacements(self) -> None:
        super()._init_replacements()
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
