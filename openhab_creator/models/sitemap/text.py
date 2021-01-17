from __future__ import annotations
from typing import Optional, List

from openhab_creator.models.sitemap.baseelement import BaseElement


class Text(BaseElement):
    def __init__(self, **args):
        super().__init__(**args)

    def dump(self) -> str:
        return super().dump('Text')
