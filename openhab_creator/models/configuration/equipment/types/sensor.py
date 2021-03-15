from __future__ import annotations

from typing import Dict, List

from openhab_creator import _, CreatorEnum
from openhab_creator.models.items import GroupType, NumberType, PropertyType
from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)


class SensorType(CreatorEnum):
    TEMPERATURE = 'temperature',\
                  _('Temperatures'), _('Temperature'), '%.1f °C', \
                  GroupType.NUMBER_AVG, NumberType.TEMPERATURE,\
                  PropertyType.TEMPERATURE

    HUMIDITY = 'humidity',\
               _('Humidity'), _('Humidity'), '%,.0f %%',\
               GroupType.NUMBER_AVG, NumberType.DIMENSIONLESS,\
               PropertyType.HUMIDITY

    PRESSURE = 'pressure',\
               _('Pressure'), _('Pressure'), '%,.1f hPa',\
               GroupType.NUMBER_AVG, NumberType.PRESSURE,\
               PropertyType.PRESSURE

    def __init__(self, point: str,
                 labelpage: str, labelitem: str, format_string: str,
                 grouptype: GroupType, numbertype: NumberType,
                 propertytype: PropertyType):
        self.point: str = point
        self.labelpage: str = labelpage
        self.labelitem: str = labelitem
        self.format_string: str = format_string
        self.grouptype: GroupType = grouptype
        self.numbertype: NumberType = numbertype
        self.propertytype = propertytype


@EquipmentType()
class Sensor(Equipment):
    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {**{
            'sensor': 'sensor'
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
