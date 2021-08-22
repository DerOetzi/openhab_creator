from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import \
        Lightbulb


class WallSwitchItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.wallswitch

    @property
    def wallswitch(self) -> str:
        return self._identifier('wallSwitch')

    @property
    def wallswitchassignment(self) -> str:
        return self._identifier('wallSwitchAssignment')

    @property
    def button(self) -> str:
        return self._identifier('wallSwitchButton')

    def buttonassignment(self, button_key: int, lightbulb: Optional[Lightbulb] = None) -> str:
        buttonassignment = self._identifier(
            f'WallSwitchAssignment{button_key}')

        if lightbulb is not None:
            buttonassignment += f'_{lightbulb.identifier}'

        return buttonassignment


@EquipmentType()
class WallSwitch(Equipment):

    def __init__(self,
                 buttons: List[Dict],
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: WallSwitchItemIdentifiers = WallSwitchItemIdentifiers(
            self)

        self.buttons: List[Dict] = buttons

    @property
    def item_ids(self) -> WallSwitchItemIdentifiers:
        return self._item_ids

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

    def buttonassignment_name(self, button_key: int) -> str:
        return _('Button {count} ({name})').format_map({
            'count': (button_key + 1),
            'name': self.buttons[button_key]['label']
        })

    @property
    def scripting(self) -> Dict[str, str]:
        scripting = {
            "trigger_channel": self.points.channel('trigger')
        }

        for button_key in range(0, self.buttons_count):
            button = self.buttons[button_key]
            for button_event in button['events']:
                scripting[f'event_{button_event}'] = self.item_ids.buttonassignment(
                    button_key)

        return scripting
