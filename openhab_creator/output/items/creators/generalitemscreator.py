from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
from openhab_creator.models.items import Group, GroupType, String
from openhab_creator.output.items import ItemsCreatorPipeline

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(0)
class GeneralItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('Config')\
            .label(_('Configuration items'))\
            .append_to(self)

        Group('Sensor')\
            .label(_('Sensor items'))\
            .append_to(self)

        Group('Auto')\
            .label(_('Scene controlled configuration items'))\
            .config()\
            .append_to(self)

        Group('LowBattery')\
            .label(_('Batteries status'))\
            .map('lowbattery')\
            .icon('lowbattery')\
            .typed(GroupType.NUMBER_MAX)\
            .append_to(self)

        String('guiPeriod')\
            .label(_('Period'))\
            .icon('period')\
            .config()\
            .append_to(self)

        self.write_file('generals')
