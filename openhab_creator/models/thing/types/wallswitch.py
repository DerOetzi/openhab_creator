from __future__ import annotations

from typing import Dict, List, Tuple, Union, Optional, TYPE_CHECKING

from openhab_creator import _
from openhab_creator.exception import BuildException
from openhab_creator.models.thing.equipment import Equipment
from openhab_creator.models.thing.equipmenttype import EquipmentType

if TYPE_CHECKING:
    from openhab_creator.models.thing.types.lightbulb import Lightbulb


@EquipmentType("wallswitch")
class WallSwitch(Equipment):
    def __init__(self,
                 typed: str,
                 config: Dict[str, Union[str, List['str']]],
                 **equipment_args: Dict):
        self._check_type(typed, 'wallswitch')

        self.__buttons: List[str] = config.pop('buttons')

        super().__init__(typed=typed, config=config, **equipment_args)

    def wallswitch_id(self) -> str:
        return self.identifier('wallSwitch')

    def wallswitchassignment_id(self) -> str:
        return self.identifier('WallSwitchAssignment')

    def button_id(self) -> str:
        return self.identifier('wallSwitchButton')

    def buttons_count(self):
        return len(self.__buttons)

    def buttonassignment_id(self, button_key: int, lightbulb: Optional[Lightbulb] = None) -> str:
        if lightbulb is None:
            return f'WallSwitchAssignment{button_key}{self._identifier}'
        else:
            return f'WallSwitchAssignment{button_key}{self._identifier}_{lightbulb.identifier()}'

    def buttonassignment_name(self, button_key: int) -> str:
        return _('Button {count} ({name})').format_map({
            'count': (button_key + 1),
            'name': self.__buttons[button_key]
        })
