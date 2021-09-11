from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import \
        Lightbulb


class PollenCountItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.pollencount

    @property
    def pollencount(self) -> str:
        return self._identifier('pollencount')


@EquipmentType()
class PollenCount(Equipment):
    def __init__(self, **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: PollenCountItemIdentifiers = PollenCountItemIdentifiers(
            self)

    @property
    def item_ids(self) -> PollenCountItemIdentifiers:
        return self._item_ids

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
