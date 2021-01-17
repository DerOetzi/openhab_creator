from __future__ import annotations

import os
from typing import TYPE_CHECKING

from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
from openhab_creator.output.items.lightbulbitemscreator import LightbulbItemsCreator
from openhab_creator.output.items.locationitemscreator import LocationItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration


class ItemsCreator(BaseItemsCreator):
    def build(self, configuration: SmarthomeConfiguration) -> None:
        self.__buildGeneral()

        locations_creator = LocationItemsCreator(
            self._outputdir, self._check_only)
        locations_creator.build(configuration)

        lightbulb_creator = LightbulbItemsCreator(
            self._outputdir, self._check_only)
        lightbulb_creator.build_items(configuration.lightbulbs())

    def __buildGeneral(self) -> None:
        self._create_group('Config', 'Configuration items')
        self._create_group('Sensor', 'Sensor items')

        self._write_file('generals')
