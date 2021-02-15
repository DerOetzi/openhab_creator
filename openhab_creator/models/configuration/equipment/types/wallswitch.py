from __future__ import annotations

from typing import Dict, List

from openhab_creator.models.configuration.equipment import Equipment, EquipmentType


@EquipmentType
class WallSwitch(Equipment):

    def __init__(self,
                 buttons: List[str],
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self.buttons: List[str] = buttons

    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'wallswitch': 'wallSwitch',
            'wallswitchassignment': 'wallSwitchAssignment',
            'button': 'wallSwitchButton'
        }
