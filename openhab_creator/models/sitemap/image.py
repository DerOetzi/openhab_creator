from __future__ import annotations

from typing import Optional

from openhab_creator.models.sitemap.baseelement import BaseElement


class Image(BaseElement):
    def __init__(self, url: str, refresh: Optional[int] = 60000):
        super().__init__()
        self.attribute('url', url, '"', '"')
        self.attribute('refresh', refresh)

    @property
    def elementtype(self) -> str:
        return 'Image'
