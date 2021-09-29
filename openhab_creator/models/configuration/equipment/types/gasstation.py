from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _, CreatorEnum
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)


class FuelType(CreatorEnum):
    DIESEL = 'diesel', _('Diesel')
    E10 = 'e10', _('E10')
    E5 = 'e5', _('E5')

    def __init__(self, identifier: str, label: str):
        self.identifier: str = identifier
        self.label: str = label


class GasStationIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.gasstation

    @property
    def gasstation(self) -> str:
        return self._identifier('gasstation')

    @property
    def price_diesel(self) -> str:
        return self._identifier('priceDiesel')

    @property
    def difference_diesel(self) -> str:
        return self._identifier('differenceDiesel')

    @property
    def price_e10(self) -> str:
        return self._identifier('priceE10')

    @property
    def difference_e10(self) -> str:
        return self._identifier('differenceE10')

    @property
    def price_e5(self) -> str:
        return self._identifier('priceE5')

    @property
    def difference_e5(self) -> str:
        return self._identifier('differenceE5')

    @property
    def opened(self) -> str:
        return self._identifier('opened')


class GasStationPoints(EquipmentPoints):
    @property
    def has_diesel(self) -> bool:
        return self.has('diesel')

    @property
    def has_e10(self) -> bool:
        return self.has('e10')

    @property
    def has_e5(self) -> bool:
        return self.has('e5')


@EquipmentType()
class GasStation(Equipment):

    def __init__(self,
                 points: Optional[Dict[str, str]],
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: GasStationIdentifiers = GasStationIdentifiers(
            self)

        self._points: GasStationPoints = GasStationPoints(points or {}, self)

    @property
    def item_ids(self) -> GasStationIdentifiers:
        return self._item_ids

    @property
    def points(self) -> GasStationPoints:
        return self._points

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('gasstation')

        for fueltype in FuelType:
            if self.points.has(fueltype.identifier):
                categories.append(fueltype.identifier)

        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Gas station")
        return f'{self.name} ({typed})'
