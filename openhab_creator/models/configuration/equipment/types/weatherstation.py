from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _, CreatorEnum
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorColors, SensorItemIdentifiers, SensorLabel, SensorPoints, SensorTyped)
from openhab_creator.models.items import NumberType, PropertyType
from openhab_creator.output.color import Color


class WeatherStationType(CreatorEnum):
    RAIN_GAUGE = 'rain_gauge',\
        SensorLabel(_('Rain gauge'), _('Rain gauge'), '%.1f mm'),\
        SensorTyped(PropertyType.RAIN, NumberType.LENGTH),\
        SensorColors([])

    CLOUDINESS = 'cloudiness',\
        SensorLabel(_('Cloudiness'), _('Cloudiness'), '%d %unit%'),\
        SensorTyped(None, NumberType.DIMENSIONLESS),\
        SensorColors([])

    SNOW = 'snow',\
        SensorLabel(_('Snow'), _('Snow'), '%.1f %uni%'),\
        SensorTyped(None, NumberType.LENGTH),\
        SensorColors([])

    VISIBILITY = 'visibility',\
        SensorLabel(_('Visibility'), _('Visibility'), '%.1f %unit%'),\
        SensorTyped(None, NumberType.LENGTH),\
        SensorColors([])

    UVINDEX = 'uvindex',\
        SensorLabel(_('UV index'), _('UV index'), '%.3f'),\
        SensorTyped(PropertyType.ULTRAVIOLET, NumberType.NONE),\
        SensorColors(outdoor=[
            (11, Color.VIOLETT), (8, Color.RED), (6, Color.ORANGE),
            (3, Color.YELLOW), (0, Color.GREEN)
        ])

    OZONE = 'ozone',\
        SensorLabel(_('Ozone'), _('Ozone'), '%.2f µg/m³', 10),\
        SensorTyped(PropertyType.OZONE, NumberType.DENSITY, 'µg/m³'),\
        SensorColors(outdoor=[
            (240, Color.RED), (180, Color.ORANGE),
            (120, Color.YELLOW), (0, Color.GREEN)
        ])

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

    @property
    def warning_active(self) -> str:
        return self._identifier('warningActive')

    @property
    def warning_severity(self) -> str:
        return self._identifier('warningSeverity')

    @property
    def warning_headline(self) -> str:
        return self._identifier('warningHeadline')

    @property
    def warning_event(self) -> str:
        return self._identifier('warningEvent')

    @property
    def warning_event_mapped(self) -> str:
        return self._identifier('warningEventMapped')

    @property
    def warning_urgency(self) -> str:
        return self._identifier('warningUrgency')

    @property
    def warning_description(self) -> str:
        return self._identifier('warningDescription')

    @property
    def warning_instruction(self) -> str:
        return self._identifier('warningInstruction')

    @property
    def warning_from(self) -> str:
        return self._identifier('warningFrom')

    @property
    def warning_to(self) -> str:
        return self._identifier('warningTo')

    @property
    def uvindex(self) -> str:
        return self._identifier('uvindex')

    @property
    def uvindex_control(self) -> str:
        return self._identifier('uvindexControl')

    def safeexposure(self, index: int) -> str:
        return self._identifier(f'safeexposure{index}')

    @property
    def ozone(self) -> str:
        return self._identifier('ozone')

    @property
    def gui_ozone(self) -> str:
        return self._identifier('guiozone')


class WeatherStationPoints(SensorPoints):
    @property
    def has_stationname(self) -> bool:
        return self.has('stationname')

    @property
    def has_condition_id(self) -> bool:
        return self.has('condition_id')

    @property
    def has_rain_gauge(self) -> bool:
        return self.has('rain_gauge', True)

    @property
    def has_warning_active(self) -> bool:
        return self.has('warning_active')

    @property
    def has_warning_severity(self) -> bool:
        return self.has('warning_severity')

    @property
    def has_warning_urgency(self) -> bool:
        return self.has('warning_urgency')

    @property
    def has_warning_description(self) -> bool:
        return self.has('warning_description')

    @property
    def has_warning_event(self) -> bool:
        return self.has('warning_event')

    @property
    def has_warning_headline(self) -> bool:
        return self.has('warning_headline')

    @property
    def has_warning_instruction(self) -> bool:
        return self.has('warning_instruction')

    @property
    def has_warning_from(self) -> bool:
        return self.has('warning_from')

    @property
    def has_warning_to(self) -> bool:
        return self.has('warning_to')

    @property
    def has_warning_updated(self) -> bool:
        return self.has('warning_updated')

    @property
    def has_uvindex(self) -> bool:
        return self.has('uvindex')

    @property
    def has_ozone(self) -> bool:
        return self.has('ozone')


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

        if self.points.has_warning_active:
            categories.append('warning')

        for weathertype in WeatherStationType:
            if self.points.has(weathertype.point):
                categories.append(weathertype.point)

        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Weatherstation")
        return f'{self.name} ({typed})'
