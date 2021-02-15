from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
from openhab_creator.output.items import ItemsCreatorPipeline

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.location.indoor.floors import Floor
    from openhab_creator.models.configuration.location.indoor.rooms import Room


@ItemsCreatorPipeline(1)
class LocationItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration):
        for floor in configuration.floors:
            self.__create_floor(floor)
            for room in floor.rooms:
                self.__create_room(room)

        self.write_file('locations')

    def __create_floor(self, floor: Floor) -> None:
        self._create_group(
            floor.identifier, floor.name, floor.category,
            tags=[floor.__class__.__name__]
        )

    def __create_room(self, room: Room) -> None:
        self._create_group(
            room.identifier, room.name, room.category,
            [room.parent.identifier], [room.__class__.__name__]
        )
