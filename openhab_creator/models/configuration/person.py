from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator.models.configuration.baseobject import BaseObject
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.smartphone import \
    Smartphone
from openhab_creator.models.configuration.equipment.types.personstate import \
    PersonState, PersonStateType

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment


class Person(BaseObject):
    def __init__(self,
                 configuration: Configuration,
                 key: int,
                 equipment: Optional[List[Dict]] = None):
        name = configuration.secrets.secret(f'person{key}', 'identifier')
        super().__init__(name)

        self.has_presence: bool = False

        self.states: Dict[str, PersonState] = {}

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

            if isinstance(equipment, PersonState):
                self.states[equipment.statetype] = equipment

    @property
    def presence_id(self) -> str:
        return f'presence{self.identifier}'

    @property
    def person_tags(self) -> Dict[str, str]:
        tags = {
            'person': self.name
        }

        return tags

    def get_state(self, statetype: PersonStateType) -> PersonState | None:
        return self.states[statetype] if statetype in self.states else None
