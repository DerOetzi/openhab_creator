from __future__ import annotations

from typing import Optional, Final, Dict, List

from openhab_creator.models.configuration.equipment import Equipment, EquipmentType


@EquipmentType
class WallSwitch(Equipment):
    ITEM_IDENTIFIERS: Final[Dict[str, str]] = {
        'wallswitch': 'wallSwitch',
        'wallswitchassignment': 'wallSwitchAssignment',
        'button': 'wallSwitchButton'
    }

    def __init__(self,
                 buttons: List[str],
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self.buttons: List[str] = buttons
