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

    @property
    def rise(self) -> str:
        return self._identifier('rise')

    @property
    def set(self) -> str:
        return self._identifier('set')

    @property
    def eclipse_total(self) -> str:
        return self._identifier('eclipseTotal')

    @property
    def eclipse_partial(self) -> str:
        return self._identifier('eclipsePartial')

    @property
    def zodiac(self) -> str:
        return self._identifier('zodiac')

    @property
    def full(self) -> str:
        return self._identifier('full')

    @property
    def phase(self) -> str:
        return self._identifier('phase')


class AstroPoints(EquipmentPoints):
    @property
    def has_azimuth(self) -> bool:
        return self.has('azimuth')

    @property
    def has_elevation(self) -> bool:
        return self.has('elevation')

    @property
    def has_rise(self) -> bool:
        return self.has('rise')

    @property
    def has_set(self) -> bool:
        return self.has('set')

    @property
    def has_eclipse_total(self) -> bool:
        return self.has('eclipse_total')

    @property
    def has_eclipse_partial(self) -> bool:
        return self.has('eclipse_partial')

    @property
    def has_zodiac(self) -> bool:
        return self.equipment.is_sun and self.has('zodiac')

    @property
    def has_full(self) -> bool:
        return self.equipment.is_moon and self.has('full')

    @property
    def has_phase(self) -> bool:
        return self.equipment.is_moon and self.has('phase')


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
    def is_sun(self) -> bool:
        return self.thing.typed == 'sun'

    @property
    def is_moon(self) -> bool:
        return self.thing.typed == 'moon'

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('astro')
        if self.is_thing:
            categories.append(self.thing.typed)
        return categories

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def name_with_type(self) -> str:
        typed = _("Astro")
        return f'{self.name} ({typed})'
