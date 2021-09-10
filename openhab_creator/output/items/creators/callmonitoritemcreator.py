from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import Call, Group, PointType, String
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.callmonitor import \
        CallMonitor


@ItemsCreatorPipeline(8)
class CallMonitorItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        has_callmonitors, callmonitors = configuration.equipment.has(
            'callmonitor')

        if has_callmonitors:
            for callmonitor in callmonitors:
                self.build_callmonitor(callmonitor)

            self.write_file('callmonitor')

    def build_callmonitor(self, callmonitor: CallMonitor) -> None:
        Group(callmonitor.item_ids.callmonitor)\
            .label(_('Call monitor {name}').format(name=callmonitor.blankname))\
            .semantic(callmonitor)\
            .append_to(self)

        String(callmonitor.item_ids.state)\
            .label(_('Call state'))\
            .map(MapTransformation.CALLSTATE)\
            .equipment(callmonitor)\
            .semantic(PointType.STATUS)\
            .channel(callmonitor.points.channel('callstate'))\
            .append_to(self)

        String(callmonitor.item_ids.laststate)\
            .label(_('Last call state'))\
            .map(MapTransformation.CALLSTATE)\
            .equipment(callmonitor)\
            .config()\
            .semantic(PointType.STATUS)\
            .append_to(self)

        Call(callmonitor.item_ids.incoming)\
            .label(_('Incoming call'))\
            .equipment(callmonitor)\
            .semantic(PointType.STATUS)\
            .channel(callmonitor.points.channel('incoming'))\
            .append_to(self)

        String(callmonitor.item_ids.lastincoming)\
            .label(_('Last incoming call'))\
            .equipment(callmonitor)\
            .semantic(PointType.STATUS)\
            .append_to(self)
