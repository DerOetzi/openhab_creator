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
        Group('Wallswitches')\
            .append_to(self)

        Group('WallswitchesAssignment')\
            .label(_('Wallswitch assignment items'))\
            .config()\
            .append_to(self)

        for wallswitch in configuration.equipment.equipment('wallswitch'):
            self._create_wallswitch_groups(wallswitch)

        self.write_file('wallswitch')

    def _create_wallswitch_groups(self, wallswitch: WallSwitch):
        Group(wallswitch.item_ids.wallswitch)\
            .label(_('Wallswitch {name}').format(name=wallswitch.name))\
            .location(wallswitch.location)\
            .semantic(wallswitch)\
            .append_to(self)

        Number(wallswitch.item_ids.button)\
            .label(_('Button state'))\
            .equipment(wallswitch)\
            .groups('Wallswitches')\
            .semantic(PointType.STATUS)\
            .channel(wallswitch.points.channel('button'))\
            .scripting(wallswitch.scripting)\
            .append_to(self)

        Group(wallswitch.item_ids.wallswitchassignment)\
            .label(_('Wallswitch assignment'))\
            .equipment(wallswitch)\
            .groups('WallswitchesAssignment')\
            .append_to(self)

        for button_key in range(0, wallswitch.buttons_count):
            Group(wallswitch.item_ids.buttonassignment(button_key))\
                .label(wallswitch.buttonassignment_name(button_key))\
                .groups(wallswitch.item_ids.wallswitchassignment)\
                .append_to(self)
