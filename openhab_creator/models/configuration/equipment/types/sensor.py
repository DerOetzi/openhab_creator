from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from openhab_creator import CreatorEnum, _
from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)
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

    def __init__(self, point: str, labels: SensorLabel,
                 typed: SensorTyped, colors: SensorColors):
        self.point: str = point
        self.labels: SensorLabel = labels
        self.typed: SensorTyped = typed
        self.colors: SensorColors = colors


@EquipmentType()
class Sensor(Equipment):
    def __init__(self, **equipment_configuration):
        super().__init__(**equipment_configuration)

        if self.is_child and self.parent.category == 'sensor':
            self.name = self.parent.name

    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {**{
            'sensor': 'sensor',
            'moisturelastwatered': 'moistureLastWatered',
            'moisturelastreminder': 'moistureLastReminder'
        }, **dict((v.point, v.point) for v in SensorType)}

    @property
    def conditional_points(self) -> List[str]:
        return [v.point for v in SensorType]

    @property
    def name_with_type(self) -> str:
        typed = _("Sensor")
        return f'{self.name} ({typed})'

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('sensor')
        categories.append(self.location.area)

        for point in self.conditional_points:
            if self.has_point_recursive(point):
                categories.append(point)

        return categories

    @property
    def sensor_is_subequipment(self) -> bool:
        return False

    @property
    def merged_sensor_id(self) -> str:
        merged_sensor_id = f'sensor{self.identifier}'
        if self.is_child and self.parent.category == 'sensor':
            merged_sensor_id = f'sensor{self.parent.identifier}'

        return merged_sensor_id
