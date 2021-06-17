from __future__ import annotations

from openhab_creator.models.items.baseitem import BaseItem


class DateTime(BaseItem):

    def dateonly(self) -> DateTime:
        self.format('%1$td.%1$tm.%1$tY')
        return self

    def dateonly_weekday(self) -> DateTime:
        self.format('%1$tA, %1$td.%1$tm.%1$tY')
        return self

    def datetime(self) -> DateTime:
        self.format('%1$td.%1$tm.%1$tY %1$tH:%1$tM')
        return self

    def timeonly(self) -> DateTime:
        self.format('%1$tH:%1$tM')
        return self

    @property
    def itemtype(self) -> str:
        return 'DateTime'
