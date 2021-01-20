from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.output.items.itemscreatorregistry import ItemsCreatorRegistry
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.thing.types.wallswitch import WallSwitch


@ItemsCreatorRegistry(2)
class WallSwitchItemsCreator(BaseItemsCreator):
    def build(self, configuration: SmarthomeConfiguration) -> None:
        self._create_group('WallswitchesAssignment', _(
            'Wallswitch assignment items'), groups=['Config'])

        for wallswitch in configuration.equipment('wallswitch'):
            self._create_wallswitch_groups(wallswitch)

        self._write_file('wallswitch')

    def _create_wallswitch_groups(self, wallswitch: WallSwitch):
        self._create_group(wallswitch.wallswitch_id(),
                           _('Wallswitch {name}').format(
                               name=wallswitch.name()),
                           groups=[wallswitch.location().identifier()],
                           tags=['WallSwitch'])

        self._create_item('Number',
                          wallswitch.button_id(),
                          _('Button state'),
                          groups=[wallswitch.wallswitch_id()],
                          tags=['Status'])

        self._create_group(wallswitch.wallswitchassignment_id(),
                           _('Wallswitch assignment'),
                           groups=[
                               wallswitch.wallswitch_id(),
                               'WallswitchesAssignment'])

        for button_key in range(0, wallswitch.buttons_count()):
            self._create_group(wallswitch.buttonassignment_id(button_key),
                               wallswitch.buttonassignment_name(button_key),
                               groups=[wallswitch.wallswitchassignment_id()])

        self._create_battery(
            wallswitch, wallswitch.wallswitch_id())
