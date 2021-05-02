from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import \
        Lightbulb


class SmartphoneItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.smartphone

    @property
    def smartphone(self) -> str:
        return self._identifier('smartphone')

    @property
    def geofence(self) -> str:
        return self._identifier('geofence')

    @property
    def distance(self) -> str:
        return self._identifier('distance')

    @property
    def accuracy(self) -> str:
        return self._identifier('accuracy')

    @property
    def position(self) -> str:
        return self._identifier('position')

    @property
    def lastseen(self) -> str:
        return self._identifier('lastSeen')


class SmartphonePoints(EquipmentPoints):
    @property
    def has_distance(self) -> bool:
        self.has('distance', True)

    @property
    def has_accuracy(self) -> bool:
        self.has('accuracy', True)

    @property
    def has_position(self) -> bool:
        self.has('accuracy', True)

    @property
    def has_lastseen(self) -> bool:
        self.has('lastseen', True)


@EquipmentType()
class Smartphone(Equipment):
    def __init__(self,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: SmartphoneItemIdentifiers = SmartphoneItemIdentifiers(
            self)
        self._points: SmartphonePoints = SmartphonePoints(points or {}, self)

    @property
    def item_ids(self) -> SmartphoneItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> SmartphonePoints:
        return self._points

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('smartphone')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Smartphone")
        return f'{self.name} ({typed})'
