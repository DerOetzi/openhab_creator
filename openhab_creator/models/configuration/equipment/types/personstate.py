from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from openhab_creator import _, CreatorEnum
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.person import Person


class PersonStateType(CreatorEnum):
    HOLIDAYS = ('holidays',
                _('Holidays'),
                'holidays',
                'Holidays',
                True,
                True)

    HOMEOFFICE = ('homeoffice',
                  _('Homeoffice'),
                  'homeoffice',
                  'Homeoffice',
                  False,
                  False)

    SICKNESS = ('sickness',
                _('Sickness'),
                'sickness',
                'Sickness',
                True,
                True)

    def __init__(self,
                 identifier: str,
                 label: str,
                 icon: str,
                 group: str,
                 has_next: bool,
                 is_freeday: bool):
        self.identifier: str = identifier
        self.label: str = label
        self.icon: str = icon
        self._group: str = group
        self.has_next: bool = has_next
        self.is_freeday: bool = is_freeday

    @property
    def group(self) -> str:
        return f'PersonState{self._group}'

    @property
    def group_tomorrow(self) -> str:
        return f'PersonStateTomorrow{self._group}'

    @classmethod
    def of_value(cls, value: str):
        of_value = None
        for enum_value in cls:
            if enum_value.identifier == value:
                of_value = enum_value
                break

        return of_value


class PersonStateItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.personstate

    @property
    def personstate(self) -> str:
        return self._identifier('personState')

    @property
    def personstate_tomorrow(self) -> str:
        return self._identifier('personStateTomorrow')

    @property
    def begin(self) -> str:
        return self._identifier('personStateBegin')

    @property
    def begin_next(self) -> str:
        return self._identifier('personStateBeginNext')


@EquipmentType()
class PersonState(Equipment):
    def __init__(self,
                 statetype: str,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids = PersonStateItemIdentifiers(self)

        self.statetype: PersonStateType = PersonStateType.of_value(statetype)

    @property
    def item_ids(self) -> PersonStateItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('personstate')
        categories.append(self.statetype.identifier)
        return categories

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def name_with_type(self) -> str:
        typed = _("Person state")
        return f'{self.name} ({typed})'
