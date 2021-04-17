from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Dict

from openhab_creator.models.configuration.location import LocationFactory
from openhab_creator.models.configuration.location.indoor import Indoor, IndoorType

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@IndoorType()
class Floor(Indoor):
    def __init__(self,
                 configuration: Configuration,
                 rooms: Optional[List[Dict]] = None,
                 **location_configuration):
        super().__init__(configuration, **location_configuration)

        self._init_rooms(configuration, [] if rooms is None else rooms)

    def _init_rooms(self, configuration: Configuration, rooms_definition: List[Dict]) -> None:
        self.rooms: List[Indoor] = []

        for room_definition in rooms_definition:
            room = LocationFactory.new(
                configuration=configuration, **room_definition)
            room.parent = self

            self.rooms.append(room)

    @property
    def typed(self) -> str:
        return 'Floor'


class FloorType(IndoorType):
    pass


@FloorType()
class Attic(Floor):
    pass


@FloorType()
class Basement(Floor):
    pass


@FloorType()
class FirstFloor(Floor):
    pass


@FloorType()
class GroundFloor(Floor):
    pass


@FloorType()
class SecondFloor(Floor):
    pass


@FloorType()
class ThirdFloor(Floor):
    pass
