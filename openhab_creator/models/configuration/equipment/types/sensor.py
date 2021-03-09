from __future__ import annotations

from typing import Optional, Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import Equipment, EquipmentType


@EquipmentType()
class Sensor(Equipment):
    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'temperature': 'temperature'
        }

    @property
    def conditional_points(self) -> List[str]:
        return ['temperature']

    @property
    def name_with_type(self) -> str:
        typed = _("Sensor")
        return f'{self.name} ({typed})'

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('sensor')
        for point in self.points:
            if self.has_point_recursive(point):
                categories.append(point)

        return categories
