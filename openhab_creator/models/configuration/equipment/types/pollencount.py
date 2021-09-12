from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator import _, CreatorEnum
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType, EquipmentPoints)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import \
        Lightbulb


class PollenType(CreatorEnum):
    ALDER = 'alder', _('Alder')
    AMBROSIA = 'ambrosia', _('Ambrosia')
    ASH = 'ash', _('Ash')
    BIRCH = 'birch', _('Birch')
    GRASSES = 'grasses', _('Grasses')
    HAZEL = 'hazel', _('Hazel')
    MUGWORT = 'mugwort', _('Mugwort')
    RYE = 'rye', _('Rye')

    def __init__(self, identifier: str, label: str):
        self.identifier: str = identifier
        self.label: str = label


class PollenCountItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.pollencount

    @property
    def pollencount(self) -> str:
        return self._identifier('pollencount')


class PollenCountPoints(EquipmentPoints):
    def __init__(self, points: str | Dict[str, str], equipment: PollenCount):
        if isinstance(points, str) and points == 'all':
            points = {}
            for pollentype in PollenType:
                points[f'{pollentype}_today'] = f'{pollentype}#today'
                points[f'{pollentype}_tomorrow'] = f'{pollentype}#tomorrow'
                points[f'{pollentype}_dayafter'] = f'{pollentype}#dayafter_to'

        super().__init__(points, equipment)

    def has_today(self, pollentype: PollenType) -> bool:
        return self.has(f'{pollentype}_today')

    def has_tomorrow(self, pollentype: PollenType) -> bool:
        return self.has(f'{pollentype}_tomorrow')

    def has_day_after_tomorrow(self, pollentype: PollenType) -> bool:
        return self.has(f'{pollentype}_dayafter')


@EquipmentType()
class PollenCount(Equipment):
    def __init__(self,
                 points: Optional[str | Dict[str, str]] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: PollenCountItemIdentifiers = PollenCountItemIdentifiers(
            self)

        self._points = PollenCountPoints(points or 'all', self)

    @property
    def item_ids(self) -> PollenCountItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> PollenCountPoints:
        return self._points

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('pollencount')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Pollen count region")
        return f'{self.name} ({typed})'
