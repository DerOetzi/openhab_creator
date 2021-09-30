from __future__ import annotations

from openhab_creator.models.items.baseitem import BaseItem
from openhab_creator import CreatorEnum


class GroupType(CreatorEnum):
    COLOR = ':Color:OR(ON,OFF)'
    DIMMER_AVG = ':Dimmer:AVG'
    NUMBER = ':Number'
    NUMBER_AVG = ':Number:AVG'
    NUMBER_MIN = ':Number:MIN'
    NUMBER_MAX = ':Number:MAX'
    ONOFF = ':Switch:OR(ON,OFF)'
    LOCATION = 'Location'


class Group(BaseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._typed: str = ''

    def typed(self, typed: GroupType) -> Group:
        self._typed = str(typed)
        return self

    @property
    def itemtype(self) -> str:
        return f'Group{self._typed}'
