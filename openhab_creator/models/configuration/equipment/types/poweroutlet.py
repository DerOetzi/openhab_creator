from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorItemIdentifiers, SensorPoints)


class PowerOutletItemIdentifiers(SensorItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.poweroutlet

    @property
    def poweroutlet(self) -> str:
        return self._identifier('poweroutlet')

    @property
    def onoff(self) -> str:
        return self._identifier('onoff')

    @property
    def power(self) -> str:
        return self._identifier('power')

    def _identifier(self, prefix: str) -> str:
        if self.equipment.is_child and self.equipment.parent.category == 'poweroutlet':
            identifier = self.equipment.parent.identifier
        else:
            identifier = self.equipment.identifier

        return f'{prefix}{identifier}'


class PowerOutletPoints(SensorPoints):
    @property
    def has_onoff(self) -> bool:
        return self.has('onoff', True)

    @property
    def has_power(self) -> bool:
        return self.has('power')


@EquipmentType()
class PowerOutlet(Sensor):
    def __init__(self,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: PowerOutletItemIdentifiers = PowerOutletItemIdentifiers(
            self)

        self._points: PowerOutletPoints = PowerOutletPoints(points or {}, self)

    @property
    def item_ids(self) -> PowerOutletItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('poweroutlet')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Power outlet")
        return f'{self.name} ({typed})'

    @property
    def sensor_is_subequipment(self) -> bool:
        return True

    @property
    def poweroutlet_is_subequipment(self) -> bool:
        return False

    @property
    def group(self) -> str:
        return 'PowerOutlet'

    @property
    def onoff_group(self) -> str | None:
        return None

    @property
    def scripting(self) -> Dict:
        return {}
