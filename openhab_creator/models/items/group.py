from __future__ import annotations
from typing import Optional

from openhab_creator.models.items.baseitem import BaseItem
from enum import Enum


class GroupType(Enum):
    NUMBER_AVG = ':Number:AVG'
    NUMBER_MAX = ':Number:MAX'
    ONOFF = ':Switch:OR(ON,OFF)'
    DIMMER_AVG = ':Dimmer:AVG'


class Group(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._typed: str = ''

    def typed(self, typed: GroupType) -> Group:
        self._typed = typed.value
        return self

    @property
    def itemtype(self) -> str:
        return f'Group{self._typed}'
