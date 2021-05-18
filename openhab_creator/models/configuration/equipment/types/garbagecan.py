from __future__ import annotations

from typing import Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)


class GarbageCanItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.garbagecan

    @property
    def garbagecan(self) -> str:
        return self._identifier('garbageCan')

    @property
    def title(self) -> str:
        return self._identifier('title')

    @property
    def begin(self) -> str:
        return self._identifier('begin')


@EquipmentType()
class GarbageCan(Equipment):
    def __init__(self,
                 message: str,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids = GarbageCanItemIdentifiers(self)

        self.message: str = message

    @property
    def item_ids(self) -> GarbageCanItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('garbagecan')
        return categories

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def name_with_type(self) -> str:
        typed = _("Garbage can")
        return f'{self.name} ({typed})'
