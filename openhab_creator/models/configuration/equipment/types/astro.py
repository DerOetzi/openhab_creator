from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)


class AstroItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.astro

    @property
    def astro(self) -> str:
        return self._identifier('astro')

    @property
    def azimuth(self) -> str:
        return self._identifier('azimuth')

    @property
    def elevation(self) -> str:
        return self._identifier('elevation')


class AstroPoints(EquipmentPoints):
    @property
    def has_azimuth(self) -> bool:
        return self.has('azimuth')

    @property
    def has_elevation(self) -> bool:
        return self.has('elevation')


@EquipmentType()
class Astro(Equipment):
    def __init__(self,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: AstroItemIdentifiers = AstroItemIdentifiers(
            self)

        self._points: AstroPoints = AstroPoints(points or {}, self)

    @property
    def item_ids(self) -> AstroItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> AstroPoints:
        return self._points

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        if self.is_thing:
            categories.append(self.thing.uid)
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Astro")
        return f'{self.name} ({typed})'
