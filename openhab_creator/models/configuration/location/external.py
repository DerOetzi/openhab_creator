from __future__ import annotations

from openhab_creator.models.configuration.location import Location, LocationType


@LocationType()
class External(Location):
    @property
    def area(self) -> str:
        return 'External'

    @property
    def typed(self) -> str:
        return 'Area'

    @property
    def semantic(self) -> str:
        return 'Location'
