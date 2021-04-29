from __future__ import annotations

from typing import Optional

from openhab_creator.models.sitemap.baseelement import BaseElement


class Mapview(BaseElement):
    def __init__(self,
                 item: str,
                 height: int,
                 label: Optional[str] = ''):
        super().__init__(item, label)

        self.attribute('height', height)

    @property
    def elementtype(self) -> str:
        return 'Mapview'
