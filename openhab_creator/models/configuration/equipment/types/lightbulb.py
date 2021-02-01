from __future__ import annotations

from typing import Optional, Dict, Final

from openhab_creator.models.configuration.equipment import Equipment, EquipmentType


@EquipmentType()
class Lightbulb(Equipment):
    def __init__(self,
                 singlebulb: Optional[bool] = False,
                 nightmode: Optional[bool] = False,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self.__SINGLEBULB: Final[bool] = singlebulb
        self.__NIGHTMODE: Final[bool] = nightmode

    @property
    def singlebulb(self) -> bool:
        return self.__SINGLEBULB

    @property
    def nightmode(self) -> bool:
        return self.__NIGHTMODE
