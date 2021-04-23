from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator.models.configuration.baseobject import BaseObject
from openhab_creator.models.configuration.equipment import EquipmentFactory

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment


class Person(BaseObject):
    def __init__(self,
                 configuration: Configuration,
                 key: int,
                 equipment: Optional[List[Dict]] = None):
        name = configuration.secrets.secret(f'person{key}')
        super().__init__(name)

        self._init_equipment(
            configuration, [] if equipment is None else equipment)

    def _init_equipment(self, configuration: Configuration, equipment: List[Dict]) -> None:
        self.equipment: List[Equipment] = []

        for equipment_definition in equipment:
            self.equipment.append(EquipmentFactory.new(configuration=configuration,
                                                       person=self,
                                                       ** equipment_definition))
