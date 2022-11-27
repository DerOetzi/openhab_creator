from __future__ import annotations

from openhab_creator.models.configuration.location import Location, LocationType


@LocationType()
class Indoor(Location):

    @property
    def area(self) -> str:
        return 'Indoor'

    @property
    def typed(self) -> str:
        return 'Area'


class IndoorType(LocationType):
    pass


@IndoorType()
class Corridor(Indoor):
    pass


