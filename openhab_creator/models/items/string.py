from __future__ import annotations

from openhab_creator.models.items.baseitem import BaseItem


class String(BaseItem):

    @property
    def itemtype(self) -> str:
        return 'String'
