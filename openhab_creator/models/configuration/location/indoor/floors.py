from __future__ import annotations

from openhab_creator.models.configuration.location.indoor import Indoor, IndoorType


@IndoorType()
class Floor(Indoor):

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
