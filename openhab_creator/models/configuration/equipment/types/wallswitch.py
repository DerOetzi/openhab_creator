from __future__ import annotations

from typing import Optional, Dict, Final, List

from openhab_creator.models.configuration.equipment import Equipment, EquipmentType


@EquipmentType()
class WallSwitch(Equipment):
    def __init__(self,
                 buttons: List[str],
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self.__BUTTONS: List[str] = buttons

    @property
    def buttons(self) -> List[str]:
        return self.__BUTTONS
