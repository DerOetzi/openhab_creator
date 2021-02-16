from __future__ import annotations

from enum import Enum
from typing import Optional

from openhab_creator.models.items.baseitem import BaseItem


class NumberType(Enum):
    DIMENSIONLESS = ':Dimensionless'
    TIME = ''  # TODO Number:Time See openhab-webui#765


class Number(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._typed: str = ''

    def percentage(self, digits: Optional[int] = 0) -> Number:
        self.typed(NumberType.DIMENSIONLESS)
        self.output(f'%.{digits}f %%')
        return self

    def typed(self, typed: NumberType) -> Number:
        self._typed = typed.value
        return self

    @property
    def itemtype(self) -> str:
        return f'Number{self._typed}'
