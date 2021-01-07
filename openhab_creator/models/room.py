from __future__ import annotations
from typing import TYPE_CHECKING

from openhab_creator.models.location import Location

if TYPE_CHECKING:
    from openhab_creator.models.floor import Floor

class Room(Location):
    VALIDTYPES = [
        "room",
        "bedroom",
        "livingroom",
        "dinningroom",
        "bathroom",
        "kitchen",
        "office",
        "corridor"
    ]

    _floor: Floor

    def __init__(self, configuration: dict, floor: Floor):
        name = configuration.get('name')

        super().__init__(name, configuration, Room.VALIDTYPES)

        self._floor = floor
        floor.addRoom(self)

    def roomstring(self) -> str:
        return 'Group %s "%s" <%s> (%s) ["Room","%s"]' % (self._id, self._name, self._icon, self._floor.id(), self._typed)

