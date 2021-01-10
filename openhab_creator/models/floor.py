from __future__ import annotations
from typing import List, TYPE_CHECKING

from openhab_creator.models.location import Location

if TYPE_CHECKING:
    from openhab_creator.models.room import Room


class Floor(Location):
    VALIDTYPES = {
        'floor':'Floor',
        'attic': 'Attic',
        'basement': 'Basement',
        'groundfloor': 'GroundFloor',
        'firstfloor': 'FirstFloor'
    }

    _rooms = []

    def __init__(self, configuration: dict):
        name = configuration.get('name')

        super().__init__(name, configuration)
        self._rooms = []

    def _default_type(self) -> str:
        return 'floor'

    def _is_valid_type(self, typed: str) -> bool:
        return typed in Floor.VALIDTYPES

    def add_room(self, room: Room):
        self._rooms.append(room)

    def rooms(self) -> List[Room]:
        return self._rooms

    def typed_formatted(self):
        return Floor.VALIDTYPES[self._typed]

class FloorManager(object):
    __registry: List[Floor]

    def __init__(self):
        self.__registry = []

    def register(self, floor: Floor) -> None:
        self.__registry.append(floor)

    def all(self) -> List[Floor]:
        return self.__registry
