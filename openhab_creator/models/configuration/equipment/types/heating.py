from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorItemIdentifiers)


class HeatingItemIdentifiers(SensorItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.heating

    @property
    def heating(self) -> str:
        return self._identifier('heating')

    @property
    def sensor(self) -> str:
        return self._identifier(f'sensor{self.equipment.semantic}')

    @property
    def heatcontrol(self) -> str:
        return self._identifier('heatcontrol')

    @property
    def auto(self) -> str:
        return self._identifier('autoHeating')

    @property
    def autodisplay(self) -> str:
        return self._identifier('autoDisplayHeating')

    @property
    def autoreactivation(self) -> str:
        return self._identifier('autoReactivationHeating')

    @property
    def heatsetpoint(self) -> str:
        return self._identifier('heatsetpoint')

    @property
    def comforttemperature(self) -> str:
        return self._identifier('comfortTemperature')

    @property
    def ecotemperature(self) -> str:
        return self._identifier('ECOTemperature')


@EquipmentType()
class Heating(Sensor):
    def __init__(self,
                 boost: Optional[bool] = False,
                 off_temp: Optional[float] = 6.0,
                 boost_temp: Optional[float] = 28.0,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self._item_ids: HeatingItemIdentifiers = HeatingItemIdentifiers(self)

        self.boost: bool = boost
        self.off_temp: float = off_temp
        self.boost_temp: float = boost_temp

    @property
    def item_ids(self) -> HeatingItemIdentifiers:
        return self._item_ids

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

    @property
    def sensor_is_subequipment(self) -> bool:
        return True

    @property
    def merged_sensor_id(self) -> str:
        return f'sensor{self.semantic}{self.identifier}'
