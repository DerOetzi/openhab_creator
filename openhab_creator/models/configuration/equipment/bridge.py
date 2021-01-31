from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Final, List, Optional

from openhab_creator.models.configuration.equipment import Equipment

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.thing import Thing


class Bridge(Equipment):
    def __init__(self,
                 configuration: Configuration,
                 name: str,
                 binding: str,
                 thing: Dict,
                 secrets: Optional[List[str]] = None):

        self.__BINDING: Final[str] = binding

        super().__init__(configuration=configuration,
                         name=name, thing=thing, secrets=secrets)

        self.__THINGS: Final[List[Thing]] = []

    @property
    def binding(self) -> str:
        return self.__BINDING

    @property
    def things(self) -> List[Thing]:
        return self.__THINGS

    def add_thing(self, thing: Thing) -> None:
        self.things.append(thing)
