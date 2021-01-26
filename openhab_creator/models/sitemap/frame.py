from __future__ import annotations
from typing import Optional, List

from openhab_creator.models.sitemap.baseelement import BaseElement


class Frame(BaseElement):
    def __init__(self, label: Optional[str] = None):
        super().__init__(label)

    def dump(self) -> str:
        if not self.has_elements():
            return ''

        return super().dump('Frame')
