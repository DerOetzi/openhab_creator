from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers)

if TYPE_CHECKING:
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

        self.parent_bridge: Optional[Bridge] = None

    @property
    def item_ids(self) -> BridgeItemIdentifiers:
        return self._item_ids

    def add_thing(self, thing: Thing) -> None:
        if (self.thing is None
                or self.thing.equipment_node.identifier != thing.equipment_node.identifier):
            self.things.append(thing)

    @property
    def name_with_type(self) -> str:
        return f'{self.name} (Bridge)'

    @property
    def is_subbridge(self) -> bool:
        return self.parent_bridge is not None
