from __future__ import annotations
from typing import TYPE_CHECKING

import os

if TYPE_CHECKING:
    from openhab_creator.models.floor import FloorManager

from openhab_creator.output.itemcreator import ItemCreator
from openhab_creator.output.locationscreator import LocationsCreator


class ItemsCreator(ItemCreator):
    def build(self, floors: FloorManager):
        locations_creator = LocationsCreator(self._outputdir, self._check_only)
        locations_creator.build(floors)
