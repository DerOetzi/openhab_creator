from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator.exception import ConfigurationException
from openhab_creator.models.location.location import Location
from openhab_creator.models.location.room import Room

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration


class Floor(Location):
    VALIDTYPES = {
        'floor': 'Floor',
        'attic': 'Attic',
        'basement': 'Basement',
        'groundfloor': 'GroundFloor',
        'firstfloor': 'FirstFloor'
    }

    def __init__(self, configuration: SmarthomeConfiguration,
                 name: str, typed: Optional[str] = 'floor', identifier: Optional[str] = None,
                 rooms: Optional[List] = [],
                 equipment: Optional[List] = []):

        if typed not in Floor.VALIDTYPES:
            raise ConfigurationException(f'No valid type "{typed} for floor"')

        super().__init__(typed, name, identifier)

        self.__rooms = []

        self._init_equipment(configuration, equipment)
        self.__init_rooms(configuration, rooms)

    def __init_rooms(self, configuration: SmarthomeConfiguration, rooms: List) -> None:
        for room_configuration in rooms:
            self.__rooms.append(
                Room(configuration=configuration, floor=self, **room_configuration))

    def rooms(self) -> List[Room]:
        return self.__rooms

    def typed_formatted(self):
        return Floor.VALIDTYPES[self._typed]
