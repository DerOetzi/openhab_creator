from __future__ import annotations

from typing import Dict, List

from openhab_creator import _, CreatorEnum
from openhab_creator.models.items import GroupType
from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)


class SensorType(CreatorEnum):
    TEMPERATURE = 'temperature', _(
        'Temperatures'), '%.1f °C', GroupType.NUMBER_AVG

    def __init__(self, point: str,
                 label: str, format_string: str,
                 grouptype: GroupType):
        self.point: str = point
        self.label: str = label
        self.format_string: str = format_string
        self.grouptype: GroupType = grouptype


@EquipmentType()
class Sensor(Equipment):
    @property
    def item_identifiers(self) -> Dict[str, str]:
        return dict((v.point, v.point) for v in SensorType)

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
