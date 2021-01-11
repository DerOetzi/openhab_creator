from __future__ import annotations
from typing import TYPE_CHECKING

from openhab_creator.models.location import Location

if TYPE_CHECKING:
    from openhab_creator.models.location.floor import Floor


class Room(Location):
    VALIDTYPES = {
        "room": "Room",
        "bedroom": "Bedroom",
        "livingroom": "LivingRoom",
        "dinningroom": "Room",
        "bathroom": "Bathroom",
        "kitchen": "Kitchen",
        "office": "Room",
        "corridor": "Corridor"
    }

    def __init__(self, configuration: dict, floor: Floor):
        name = configuration.get('name')

        super().__init__(name, configuration)

        self.__floor: Floor = floor
        floor.add_room(self)

    def _default_type(self) -> str:
        return 'room'

    def _is_valid_type(self, typed: str) -> bool:
        return typed in Room.VALIDTYPES

    def floor(self) -> Floor:
        return self.__floor

    def typed_formatted(self):
        return Room.VALIDTYPES[self._typed]
