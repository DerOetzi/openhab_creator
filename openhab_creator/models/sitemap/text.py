from __future__ import annotations

from openhab_creator.models.sitemap.baseelement import BaseElement


class Text(BaseElement):

    @property
    def elementtype(self) -> str:
        return 'Text'
