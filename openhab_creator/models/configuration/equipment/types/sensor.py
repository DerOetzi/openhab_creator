from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from openhab_creator import CreatorEnum, _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)
from openhab_creator.models.items import NumberType, PropertyType
from openhab_creator.output import Color


@dataclass
class SensorLabel:
    page: str
    item: str
    format_str: str
    gui_factor: Optional[int] = None

    @property
    def has_gui_factor(self) -> bool:
        return self.gui_factor is not None


@dataclass
class SensorTyped:
    property: PropertyType
    number: NumberType


class SensorColors:
    def __init__(self, indoor: List[Tuple[int, Color]]):
        self.indoor: List[Tuple[int, Color]] = indoor

    @property
    def has_indoor(self) -> bool:
        return len(self.indoor) > 0

    def indoor_colors(self, item: str) -> List[Tuple[str, Color]]:
        valuecolors = []

        for valuecolor in self.indoor:
            valuecolors.append((f'{item}>={valuecolor[0]}', valuecolor[1]))

        return valuecolors


class SensorType(CreatorEnum):
    TEMPERATURE = 'temperature',\
                  SensorLabel(_('Temperatures'), _('Temperature'), '%.1f °C'),\
                  SensorTyped(PropertyType.TEMPERATURE,
                              NumberType.TEMPERATURE),\
        SensorColors([
            (28, Color.RED), (24, Color.ORANGE), (20, Color.YELLOW),
            (16, Color.GREEN), (8, Color.BLUE), (0, Color.GREY)
        ])

    HUMIDITY = 'humidity',\
               SensorLabel(_('Humidity'), _('Humidity'), '%,.0f %%'),\
               SensorTyped(PropertyType.HUMIDITY, NumberType.DIMENSIONLESS),\
               SensorColors([
                   (60, Color.RED), (58, Color.ORANGE), (54, Color.YELLOW),
                   (42, Color.GREEN), (40, Color.ORANGE), (0, Color.RED)
               ])

    PRESSURE = 'pressure',\
               SensorLabel(_('Pressure'), _('Pressure'), '%,.1f hPa'),\
               SensorTyped(PropertyType.PRESSURE, NumberType.PRESSURE),\
               SensorColors([])

    CO2 = 'co2',\
        SensorLabel(_('CO2 concentration'), _('CO2 concentration'), '%,d ppm', 100),\
        SensorTyped(PropertyType.CO2, NumberType.DIMENSIONLESS),\
        SensorColors([
            (2000, Color.RED), (1200, Color.ORANGE), (800, Color.YELLOW),
            (0, Color.GREEN)
        ])

    MOISTURE = 'moisture',\
               SensorLabel(_('Soil moisture'), _('Soil moisture'), '%,.0f %%'),\
               SensorTyped(PropertyType.HUMIDITY, NumberType.DIMENSIONLESS),\
               SensorColors([
                   (85, Color.RED), (75, Color.ORANGE), (50, Color.GREEN),
                   (40, Color.YELLOW), (30, Color.ORANGE), (0, Color.RED)
               ])

    NOISE = 'noise',\
            SensorLabel(_('Noise'),  _('Noise'), '%,d dB'),\
            SensorTyped(PropertyType.NOISE, NumberType.DIMENSIONLESS),\
            SensorColors([])

    HUMIDEX = 'humidex',\
        SensorLabel(_('Felt temperatures (Humidex)'), _('Felt temperature (Humidex)'), '%.1f °C'),\
        SensorTyped(PropertyType.TEMPERATURE, NumberType.TEMPERATURE),\
        SensorColors([])

    def __init__(self, point: str, labels: SensorLabel,
                 typed: SensorTyped, colors: SensorColors):
        self.point: str = point
        self.labels: SensorLabel = labels
        self.typed: SensorTyped = typed
        self.colors: SensorColors = colors


class SensorItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.sensor

    @property
    def sensor(self) -> str:
        return self._identifier('sensor')

    @property
    def merged_sensor(self) -> str:
        if self.equipment.is_child and self.equipment.parent.category == 'sensor':
            merged_sensor_id = self.equipment.parent.item_ids.sensor
        else:
            merged_sensor_id = self.sensor

        return merged_sensor_id

    @property
    def temperature(self) -> str:
        return f'temperature{self.merged_sensor}'

    @property
    def humidity(self) -> str:
        return f'humidity{self.merged_sensor}'

    @property
    def pressure(self) -> str:
        return f'pressure{self.merged_sensor}'

    @property
    def pressure_sealevel(self) -> str:
        return f'pressureSeaLevel{self.merged_sensor}'

    @property
    def co2(self) -> str:
        return f'co2{self.merged_sensor}'

    @property
    def moisture(self) -> str:
        return f'moisture{self.merged_sensor}'

    @property
    def moisturelastwatered(self) -> str:
        return self._identifier('moistureLastWatered')

    @property
    def moisturelastreminder(self) -> str:
        return self._identifier('moistureLastReminder')

    @property
    def noise(self) -> str:
        return f'noise{self.merged_sensor}'

    @property
    def humidex(self) -> str:
        return f'humidex{self.merged_sensor}'


class SensorPoints(EquipmentPoints):
    @property
    def has_temperature(self) -> str:
        return self.has('temperature', True)

    @property
    def has_humidity(self) -> str:
        return self.has('humidity', True)

    @property
    def has_pressure(self) -> str:
        return self.has('pressure', True)

    @property
    def has_co2(self) -> str:
        return self.has('co2', True)

    @property
    def has_moisture(self) -> str:
        return self.has('moisture', True)

    @property
    def has_noise(self) -> str:
        return self.has('noise', True)

    @property
    def has_humidex(self) -> str:
        return self.has('humidex', True)


@EquipmentType()
class Sensor(Equipment):
    def __init__(self,
                 altitude: Optional[int] = None,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self.altitude: Optional[int] = altitude

        if self.is_child and self.parent.category == 'sensor':
            self.name = self.parent.name

        self._item_ids: SensorItemIdentifiers = SensorItemIdentifiers(self)
        self._points: SensorPoints = SensorPoints(points or {}, self)

    @property
    def item_ids(self) -> SensorItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> SensorPoints:
        return self._points

    @property
    def name_with_type(self) -> str:
        typed = _("Sensor")
        return f'{self.name} ({typed})'

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('sensor')
        if self.has_location:
            categories.append(self.location.area)
        elif self.has_person:
            categories.append(self.person.name)

        for sensortype in SensorType:
            if self.points.has(sensortype.point, True):
                categories.append(sensortype.point)

        return categories

    @property
    def has_altitude(self) -> bool:
        has_altitude = self.altitude is not None

        for subequipment in self.subequipment:
            has_altitude = has_altitude or subequipment.has_altitude

        return has_altitude

    @property
    def sensor_is_subequipment(self) -> bool:
        return False
