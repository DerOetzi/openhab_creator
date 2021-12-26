from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.person import Person


class PersonStateItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.personstate

    @property
    def personstate(self) -> str:
        return self._identifier('personState')

    @property
    def begin(self) -> str:
        return self._identifier('personStateBegin')


@EquipmentType()
class PersonState(Equipment):
    def __init__(self,
                 statetype: str,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids = PersonStateItemIdentifiers(self)

        self.statetype: str = statetype

    @property
    def item_ids(self) -> PersonStateItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('personstate')
        categories.append(self.statetype)
        return categories

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def name_with_type(self) -> str:
        typed = _("Person state")
        return f'{self.name} ({typed})'
