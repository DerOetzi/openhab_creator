from __future__ import annotations

from typing import Dict, Optional

from openhab_creator import _
from openhab_creator.models.common.maptransformation import BaseMapTransformation
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)


class CarItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.car

    @property
    def car(self) -> str:
        return self._identifier('car')

    @property
    def last_update(self) -> str:
        return self._identifier('carLastUpdate')

    @property
    def vehicle_locked(self) -> str:
        return self._identifier('carVehicleLocked')

    @property
    def doors_closed(self) -> str:
        return self._identifier('carDoorsClosed')

    @property
    def windows_closed(self) -> str:
        return self._identifier('carWindowsClosed')

    @property
    def climater(self) -> str:
        return self._identifier('carClimater')

    @property
    def climater_control(self) -> str:
        return self._identifier('carClimaterControl')

    @property
    def climater_target_temperature(self) -> str:
        return self._identifier('carClimaterTargetTemperature')

    @property
    def climater_state(self) -> str:
        return self._identifier('carClimaterState')

    @property
    def climater_remaining_time(self) -> str:
        return self._identifier('carClimaterRemainingTime')
    
    @property
    def climater_window_heating(self) -> str:
        return self._identifier('carClimaterWindowHeating')
    
    @property
    def charger_control(self) -> str:
        return self._identifier('carChargerControl')


class CarPoints(EquipmentPoints):
    @property
    def has_odometer(self) -> bool:
        return self.has('odometer')

    @property
    def has_last_update(self) -> bool:
        return self.has('lastUpdate')

    @property
    def has_vehicle_locked(self) -> bool:
        return self.has('vehicleLocked')

    @property
    def has_doors_closed(self) -> bool:
        return self.has('doorsClosed')

    @property
    def has_windows_closed(self) -> bool:
        return self.has('windowsClosed')

    @property
    def has_climater_control(self) -> bool:
        return self.has('climaterControl')

    @property
    def has_climater_target_temperature(self) -> bool:
        return self.has('climaterTargetTemperature')

    @property
    def has_climater_state(self) -> bool:
        return self.has('climaterState')

    @property
    def has_climater_remaining_time(self) -> bool:
        return self.has('climaterRemainingTime')

    @property
    def has_climater_window_heating(self) -> bool:
        return self.has('climaterWindowHeating')
    
    @property
    def has_charger_control(self) -> bool:
        return self.has('chargerControl')


class CarMapTransformations(BaseMapTransformation):
    VEHICLE_LOCKED = 'carvehiclelocked', {
        'ON': _('Locked'),
        'OFF': _('Unlocked')
    }

    DOORS_CLOSED = 'cardoorsclosed', {
        'ON': _('Closed'),
        'OFF': _('Open'),
    }

    WINDOWS_CLOSED = 'carwindowsclosed', {
        'ON': _('Closed'),
        'OFF': _('Open'),
    }


@EquipmentType()
class Car(Equipment):
    def __init__(self,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self._item_ids: CarItemIdentifiers = CarItemIdentifiers(self)
        self._points = CarPoints(points or {}, self)

    @property
    def item_ids(self) -> CarItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> CarPoints:
        return self._points

    @property
    def categories(self) -> list[str]:
        categories = super().categories
        categories.append('car')
        return categories

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def has_climater(self) -> bool:
        return (
            self.points.has_climater_control or
            self.points.has_climater_state or
            self.points.has_climater_target_temperature or
            self.points.has_climater_remaining_time or
            self.points.has_climater_window_heating
        )

    @property
    def name_with_type(self) -> str:
        typed = _("Car")
        return f'{self.name} ({typed})'
