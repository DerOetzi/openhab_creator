from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import Lightbulb


@EquipmentType()
class WallSwitch(Equipment):

    def __init__(self,
                 buttons: List[str],
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self.buttons: List[str] = buttons

    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'wallswitch': 'wallSwitch',
            'wallswitchassignment': 'wallSwitchAssignment',
            'button': 'wallSwitchButton'
        }

    @property
    def conditional_points(self) -> List[str]:
        return []

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('wallswitch')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Wallswitch")
        return f'{self.name} ({typed})'

    @property
    def buttons_count(self) -> int:
        return len(self.buttons)

    def buttonassignment_id(self, button_key: int, lightbulb: Optional[Lightbulb] = None) -> str:
        if lightbulb is None:
            return f'WallSwitchAssignment{button_key}{self.identifier}'
        else:
            return f'WallSwitchAssignment{button_key}{self.identifier}_{lightbulb.identifier}'

    def buttonassignment_name(self, button_key: int) -> str:
        return _('Button {count} ({name})').format_map({
            'count': (button_key + 1),
            'name': self.buttons[button_key]
        })
