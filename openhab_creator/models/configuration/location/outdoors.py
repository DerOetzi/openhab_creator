from __future__ import annotations

from openhab_creator.models.configuration.location import Location, LocationType


@LocationType()
class Outdoor(Location):

    @property
    def area(self) -> str:
        return 'Outdoor'

    @property
    def typed(self) -> str:
        return 'Area'


class OutdoorType(LocationType):
    pass


@OutdoorType()
class Carport(Outdoor):
    pass


@OutdoorType()
class Driveway(Outdoor):
    pass


@OutdoorType()
class Garden(Outdoor):
    pass


@OutdoorType()
class Patio(Outdoor):
    pass


@OutdoorType()
class Porch(Outdoor):
    pass


@OutdoorType()
class Terrace(Outdoor):
    pass
