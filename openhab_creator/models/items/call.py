from __future__ import annotations

from openhab_creator.models.items.baseitem import BaseItem


class Call(BaseItem):

    @property
    def itemtype(self) -> str:
        return 'Call'
