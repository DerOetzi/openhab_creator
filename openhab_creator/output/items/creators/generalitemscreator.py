from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
from openhab_creator.models.items import Group, GroupType
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
            .label(_('Low battery status items'))\
            .icon('lowbattery')\
            .typed(GroupType.NUMBER_AVG)\
            .append_to(self)

        self.write_file('generals')
