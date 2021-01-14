from __future__ import annotations
from typing import TYPE_CHECKING

import os

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration

from openhab_creator.output.itemcreator import ItemCreator
from openhab_creator.output.locationscreator import LocationsCreator
from openhab_creator.output.equipment.lightbulbcreator import LightbulbCreator


class ItemsCreator(ItemCreator):
    def build(self, configuration: SmarthomeConfiguration) -> None:
        self.__buildGeneral()

        locations_creator = LocationsCreator(self._outputdir, self._check_only)
        locations_creator.build(configuration)

        lightbulb_creator = LightbulbCreator(self._outputdir, self._check_only)
        lightbulb_creator.build(configuration.lightbulbs())

    def __buildGeneral(self) -> None:
        self._create_group('Config', 'Configuration items')
        self._create_group('Sensor', 'Sensor items')

        self._write_file('generals')
