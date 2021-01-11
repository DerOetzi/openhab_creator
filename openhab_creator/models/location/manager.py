from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from openhab_creator.models.location.floor import Floor


class LocationManager(object):
    def __init__(self):
        self.__floors: List[Floor] = []

    def register_floor(self, floor: Floor) -> None:
        self.__floors.append(floor)

    def floors(self) -> List[Floor]:
        return self.__floors
