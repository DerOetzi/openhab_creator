from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import Group, Number, PointType
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.wallswitch import WallSwitch


@ItemsCreatorPipeline(3)
class WallSwitchItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('WallswitchesAssignment')\
            .label(_('Wallswitch assignment items'))\
            .config()\
            .append_to(self)

        for wallswitch in configuration.equipment('wallswitch'):
            self._create_wallswitch_groups(wallswitch)

        self.write_file('wallswitch')

    def _create_wallswitch_groups(self, wallswitch: WallSwitch):
        Group(wallswitch.wallswitch_id)\
            .label(_('Wallswitch {name}').format(name=wallswitch.name))\
            .location(wallswitch.location)\
            .semantic(wallswitch)\
            .append_to(self)

        Number(wallswitch.button_id)\
            .label(_('Button state'))\
            .groups(wallswitch.wallswitch_id)\
            .semantic(PointType.STATUS)\
            .channel(wallswitch.channel('button'))\
            .append_to(self)

        Group(wallswitch.wallswitchassignment_id)\
            .label(_('Wallswitch assignment'))\
            .groups('WallswitchesAssignment', wallswitch.wallswitch_id)\
            .append_to(self)

        for button_key in range(0, wallswitch.buttons_count):
            Group(wallswitch.buttonassignment_id(button_key))\
                .label(wallswitch.buttonassignment_name(button_key))\
                .groups(wallswitch.wallswitchassignment_id)\
                .append_to(self)

        self._create_battery(wallswitch, wallswitch.wallswitch_id)
