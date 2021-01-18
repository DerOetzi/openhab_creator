from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator.models.baseobject import BaseObject

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.thing.equipment import Equipment


class Location(BaseObject):
    def __init__(self, typed: str, name: str, identifier: Optional[str] = None):
        super().__init__(typed, name, identifier)

        self._equipment: List[Equipment] = []

    def _init_equipment(self, configuration: SmarthomeConfiguration, equipment: List[Dict]):
        for equipment_config in equipment:
            self._equipment.append(
                self._equipment.append(configuration.equipment_factory(equipment_config, self)))
