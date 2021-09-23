from __future__ import annotations

from typing import Optional

from openhab_creator.models.sitemap.baseelement import BaseElement


class Slider(BaseElement):
    def __init__(self,
                 item: str,
                 min_value: int,
                 max_value: int,
                 step: Optional[float] = 1,
                 label: Optional[str] = ''):
        super().__init__(item, label)

        self.attribute('minValue', min_value)
        self.attribute('maxValue', max_value)
        self.attribute('step', step)

    @property
    def elementtype(self) -> str:
        return 'Slider'
