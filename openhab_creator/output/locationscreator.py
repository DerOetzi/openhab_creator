from __future__ import annotations
from typing import TYPE_CHECKING

from openhab_creator.output.itemcreator import ItemCreator

if TYPE_CHECKING:
    from openhab_creator.models.floor import Floor, FloorManager
    from openhab_creator.models.room import Room


class LocationsCreator(ItemCreator):
    def build(self, floors: FloorManager):
        for floor in floors.all():
            self.__create_floor(floor)
            for room in floor.rooms():
                self.__create_room(room)

        self._write_file('locations')

    def __create_floor(self, floor: Floor) -> None:
        self._create_group(
            floor.id(), floor.name(), floor.icon(),
            tags=[floor.typed_formatted()]
        )

    def __create_room(self, room: Room) -> None:
        self._create_group(
            room.id(), room.name(), room.icon(),
            [room.floor().id()], [room.typed_formatted()]
        )
