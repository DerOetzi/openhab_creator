from __future__ import annotations

from openhab_creator.models.items.baseitem import BaseItem


class Location(BaseItem):
    def __init__(self, name: str):
        super().__init__(name)
        self.format('%2$s°N %3$s°E')

    @property
    def itemtype(self) -> str:
        return 'Location'
