from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import Lightbulb


@EquipmentType()
class Smartphone(Equipment):
    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'smartphone': 'smartphone',
            'geofence': 'geofence',
            'distance': 'distance',
            'location': 'location',
            'lastseen': 'lastSeen'
        }

    @property
    def conditional_points(self) -> List[str]:
        return ['distance']

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('smartphone')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Smartphone")
        return f'{self.name} ({typed})'
