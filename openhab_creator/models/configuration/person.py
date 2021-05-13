from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator.models.configuration.baseobject import BaseObject
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.smartphone import Smartphone

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

        self.has_presence: bool = False

        self._init_equipment(configuration, equipment or [])

    def _init_equipment(self, configuration: Configuration, equipment: List[Dict]) -> None:
        self.equipment: List[Equipment] = []

        for equipment_definition in equipment:
            equipment = EquipmentType.new(configuration=configuration,
                                          person=self,
                                          **equipment_definition)

            self.equipment.append(equipment)

            self.has_presence = self.has_presence \
                or isinstance(equipment, Smartphone)

    @property
    def presence_id(self) -> str:
        return f'presence{self.identifier}'

    @property
    def person_tags(self) -> Dict[str, str]:
        tags = {
            'person': self.name
        }

        return tags
