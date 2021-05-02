from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers)

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.thing import Thing


class BridgeItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self._identifier('bridge')


class Bridge(Equipment):
    def __init__(self,
                 binding: str,
                 **equipment_configuration):

        self.binding: str = binding

        super().__init__(**equipment_configuration)

        self._item_ids = BridgeItemIdentifiers(self)

        self.things: List[Thing] = []

    @property
    def item_ids(self) -> BridgeItemIdentifiers:
        return self._item_ids

    def add_thing(self, thing: Thing) -> None:
        self.things.append(thing)

    @property
    def name_with_type(self) -> str:
        return f'{self.name} (Bridge)'
