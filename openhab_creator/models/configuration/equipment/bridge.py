from __future__ import annotations

from typing import Final, Dict, List, Optional

from openhab_creator.exception import RegistryException
from openhab_creator.models.configuration.equipment import Equipment


class Bridge(Equipment):
    def __init__(self,
                 name: str,
                 binding: str,
                 thing: Dict,
                 secrets: Optional[List[str]] = None):

        super().__init__(name=name, thing=thing, secrets=secrets)

        self.__BINDING: Final[str] = binding

    @property
    def binding(self) -> str:
        return self.__BINDING
