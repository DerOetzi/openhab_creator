from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _, CreatorEnum
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorColors, SensorItemIdentifiers, SensorLabel, SensorPoints, SensorTyped)
from openhab_creator.models.items import NumberType, PropertyType


class WeatherStationType(CreatorEnum):
    RAIN_GAUGE = 'rain_gauge',\
        SensorLabel(_('Rain gauge'), _('Rain gauge'), '%.1f mm'),\
        SensorTyped(PropertyType.RAIN, NumberType.LENGTH),\
        SensorColors([])

    def __init__(self, point: str, labels: SensorLabel,
                 typed: SensorTyped, colors: SensorColors):
        self.point: str = point
        self.labels: SensorLabel = labels
        self.typed: SensorTyped = typed
        self.colors: SensorColors = colors


class WeatherStationItemIdentifiers(SensorItemIdentifiers):
    @property
    def sensor(self) -> str:
        return self.weatherstation

    @property
    def weatherstation(self) -> str:
        return self._identifier('weatherStation')

    @property
    def condition(self) -> str:
        return self._identifier('weatherCondition')

    @property
    def rain_gauge(self) -> str:
        return self._identifier('rain_gauge')


class WeatherStationPoints(SensorPoints):
    @property
    def has_stationname(self) -> bool:
        return self.has('stationname')

    @property
    def has_condition_id(self) -> bool:
        return self.has('condition_id')

    @property
    def has_rain_gauge(self) -> str:
        return self.has('rain_gauge', True)


@EquipmentType()
class WeatherStation(Sensor):
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

        if self.points.has_condition_id:
            categories.append('condition_id')

        for weathertype in WeatherStationType:
            if self.points.has(weathertype.point):
                categories.append(weathertype.point)

        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Weatherstation")
        return f'{self.name} ({typed})'
