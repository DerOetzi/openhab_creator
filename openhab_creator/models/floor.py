from __future__ import annotations
from typing import List, TYPE_CHECKING

from openhab_creator.models.location import Location

if TYPE_CHECKING:
    from openhab_creator.models.room import Room


class Floor(Location):
    VALIDTYPES = [
        'floor',
        'attic',
        'basement',
        'groundfloor',
        'firstfloor'
    ]

    _rooms = []

    def __init__(self, configuration: dict):
        name = configuration.get('name')

        super().__init__(name, configuration, Floor.VALIDTYPES)
        self._rooms = []

    def addRoom(self, room: Room):
        self._rooms.append(room)

    def rooms(self) -> List[Room]:
        return self._rooms

    def floorstring(self) -> str:
        return 'Group %s "%s" <%s> ["Floor", "%s"]' % (self._id, self._name, self._icon, self._typed)
