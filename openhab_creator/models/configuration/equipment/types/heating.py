from __future__ import annotations

from typing import Optional, Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.sensor import Sensor


@EquipmentType()
class Heating(Sensor):
    def __init__(self,
                 boost: Optional[bool] = False,
                 off_temp: Optional[float] = 6.0,
                 boost_temp: Optional[float] = 28.0,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self.boost: bool = boost
        self.off_temp: float = off_temp
        self.boost_temp: float = boost_temp

    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'heating': 'heating',
            'heatcontrol': 'heatcontrol',
            'auto': 'autoHeating',
            'autodisplay': 'autoDisplayHeating',
            'autoreactivation': 'autoReactivationHeating',
            'heatsetpoint': 'heatsetpoint'
        }

    @property
    def conditional_points(self) -> List[str]:
        return []

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('heating')
        return categories

    @property
    def is_timecontrolled(self) -> bool:
        return True

    @property
    def semantic(self) -> str:
        return 'HVAC'

    @property
    def name_with_type(self) -> str:
        typed = _("Heating")
        return f'{self.name} ({typed})'
