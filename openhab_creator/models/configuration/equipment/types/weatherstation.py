from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)


class WeatherStationItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.weatherstation

    @property
    def weatherstation(self) -> str:
        return self._identifier('weatherStation')


class WeatherStationPoints(EquipmentPoints):
    @property
    def has_stationname(self) -> bool:
        return self.has('stationname')


@EquipmentType()
class WeatherStation(Equipment):
    def __init__(self,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: WeatherStationItemIdentifiers = WeatherStationItemIdentifiers(
            self)
        self._points: WeatherStationPoints = WeatherStationPoints(
            points or {}, self)

    @property
    def item_ids(self) -> WeatherStationItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> WeatherStationPoints:
        return self._points

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('weatherstation')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Weatherstation")
        return f'{self.name} ({typed})'
