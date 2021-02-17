from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator.models.items import Group
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.location.indoor.floors import Floor
    from openhab_creator.models.configuration.location.indoor.rooms import Room


@ItemsCreatorPipeline(1)
class LocationItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration):
        for floor in configuration.floors:
            self._create_floor(floor)
            for room in floor.rooms:
                self._create_room(room)

        self.write_file('locations')

    def _create_floor(self, floor: Floor) -> None:
        Group(floor.identifier)\
            .label(floor.name)\
            .icon(floor.category)\
            .semantic(floor)\
            .append_to(self)

    def _create_room(self, room: Room) -> None:
        Group(room.identifier)\
            .label(room.name)\
            .icon(room.category)\
            .groups(room.parent.identifier)\
            .semantic(room)\
            .append_to(self)
