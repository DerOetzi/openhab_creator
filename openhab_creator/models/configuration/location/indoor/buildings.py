from __future__ import annotations

from openhab_creator.models.configuration.location.indoor import (Indoor,
                                                                  IndoorType)


@IndoorType()
class Building(Indoor):
    @property
    def area(self) -> str:
        return 'Building'

    @property
    def typed(self) -> str:
        return 'Building'


class BuildingType(IndoorType):
    pass


@BuildingType()
class Garage(Building):
    pass


@BuildingType()
class House(Building):
    pass


@BuildingType()
class Shed(Building):
    pass


@BuildingType()
class SummerHouse(Building):
    pass
