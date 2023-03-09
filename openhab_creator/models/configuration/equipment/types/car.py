from __future__ import annotations

from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)


class CarItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.car

    @property
    def car(self) -> str:
        return self._identifier('car')


class CarPoints(EquipmentPoints):
    @property
    def has_odometer(self) -> bool:
        return self.has('odometer')


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
    def name_with_type(self) -> str:
        typed = _("Car")
        return f'{self.name} ({typed})'
