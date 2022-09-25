from __future__ import annotations

from typing import Dict, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorItemIdentifiers, SensorPoints)


class WindowItemIdentifiers(SensorItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.window

    @property
    def window(self) -> str:
        return self._identifier('window')

    @property
    def sensor(self) -> str:
        return self._identifier(f'sensor{self.equipment.semantic}')

    @property
    def windowopen(self) -> str:
        return self._identifier('windowOpen')

    @property
    def remindertime(self) -> str:
        return self._identifier('windowRemindertime')


@EquipmentType()
class Window(Sensor):
    def __init__(self,
                 remindertime: Optional[bool] = False,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: WindowItemIdentifiers = WindowItemIdentifiers(self)
        self.remindertime: bool = remindertime

    @property
    def item_ids(self) -> WindowItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('window')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Window")
        return f'{self.name} ({typed})'

    @property
    def sensor_is_subequipment(self) -> bool:
        return True
