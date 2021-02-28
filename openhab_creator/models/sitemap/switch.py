from __future__ import annotations

from typing import List, Optional, Tuple

from openhab_creator.output.formatter import Formatter
from openhab_creator.models.sitemap.baseelement import BaseElement


class Switch(BaseElement):
    def __init__(self,
                 item: str,
                 mappings: List[Tuple[str, str]],
                 label: Optional[str] = ''):
        super().__init__(item, label)

        self.attribute(
            'mappings',
            Formatter.key_value_tuples(mappings, separator=",\n            "),
            '[', ']')

    @property
    def elementtype(self) -> str:
        return 'Switch'


class Selection(Switch):
    @property
    def elementtype(self) -> str:
        return 'Selection'
