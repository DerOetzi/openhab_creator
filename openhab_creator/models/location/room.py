from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List

from openhab_creator.exception import ConfigurationException
from openhab_creator.models.location.location import Location

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.location.floor import Floor


class Room(Location):
    VALIDTYPES = {
        "room": "Room",
        "bathroom": "Bathroom",
        "bedroom": "Bedroom",
        "boilerroom": "BoilerRoom",
        "cellar": "Cellar",
        "corridor": "Corridor",
        "diningroom": "DiningRoom",
        "entry": "Entry",
        "familyroom": "FamilyRoom",
        "guestroom": "GuestRoom",
        "kitchen": "Kitchen",
        "laundryroom": "LaundryRoom",
        "livingroom": "LivingRoom",
        "office": "Office",
        "veranda": "Veranda"
    }

    def __init__(self, configuration: SmarthomeConfiguration, floor: Floor,
                 name: str, typed: Optional[str] = 'room', identifier: Optional[str] = None,
                 equipment: Optional[List] = []):

        if typed not in Room.VALIDTYPES:
            raise ConfigurationException(f'No valid type "{typed} for room"')

        super().__init__(typed, name, identifier)

        self.__floor: Floor = floor

        self._init_equipment(configuration, equipment)

    def floor(self) -> Floor:
        return self.__floor

    def typed_formatted(self):
        return Room.VALIDTYPES[self._typed]
