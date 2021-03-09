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

        self.binding: str = binding

        super().__init__(configuration=configuration,
                         name=name, thing=thing, secrets=secrets)

        self.things: List[Thing] = []

    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {}

    @property
    def conditional_points(self) -> List[str]:
        return []

    def add_thing(self, thing: Thing) -> None:
        self.things.append(thing)

    @property
    def name_with_type(self) -> str:
        return f'{self.name} (Bridge)'
