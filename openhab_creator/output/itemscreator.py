from __future__ import annotations
from typing import TYPE_CHECKING

import os

if TYPE_CHECKING:
    from openhab_creator.models.floor import FloorManager

from openhab_creator.output.basecreator import BaseCreator


class ItemsCreator(BaseCreator):
    def __init__(self, outputdir: str, check_only: bool = False):
        super().__init__('items', outputdir, check_only)

    def buildLocations(self, floors: FloorManager):
        lines = []
        for floor in floors.all():
            lines.append(floor.floorstring())
            for room in floor.rooms():
                lines.append(room.roomstring())

        self._write_file('locations', lines)
