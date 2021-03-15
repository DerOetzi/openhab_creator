from __future__ import annotations

from typing import Optional

from openhab_creator import CreatorEnum
from openhab_creator.models.items.baseitem import BaseItem


class NumberType(CreatorEnum):
    DIMENSIONLESS = ':Dimensionless'
    PRESSURE = ':Pressure'
    TEMPERATURE = ':Temperature'
    TIME = ''  # TODO Number:Time See openhab-webui#765


class Number(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._typed: str = ''

    def percentage(self, digits: Optional[int] = 0) -> Number:
        self.typed(NumberType.DIMENSIONLESS)
        self.format(f'%.{digits}f %%')
        return self

    def temperature(self, digits: Optional[int] = 1) -> Number:
        self.typed(NumberType.TEMPERATURE)
        self.format(f'%.{digits}f %unit%')
        return self

    def typed(self, typed: NumberType) -> Number:
        self._typed = str(typed)
        return self

    @property
    def itemtype(self) -> str:
        return f'Number{self._typed}'
