from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import Call, Group, PointType, String, ProfileType
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
            Group('CallState')\
                .append_to(self)

            for callmonitor in callmonitors:
                callstate_item = self.build_callmonitor(callmonitor)
                self._connect_channel_with_phonebook(
                    callmonitor, callstate_item, configuration)

            self.write_file('callmonitor')

    def build_callmonitor(self, callmonitor: CallMonitor) -> Call:
        Group(callmonitor.item_ids.callmonitor)\
            .label(_('Call monitor {name}').format(name=callmonitor.blankname))\
            .semantic(callmonitor)\
            .append_to(self)

        callstate_item = String(callmonitor.item_ids.state)\
            .label(_('Call state'))\
            .map(MapTransformation.CALLSTATE)\
            .equipment(callmonitor)\
            .groups('CallState')\
            .semantic(PointType.STATUS)\
            .scripting({
                'laststate_item': callmonitor.item_ids.laststate,
                'incoming_item': callmonitor.item_ids.incoming,
                'lastincoming_item': callmonitor.item_ids.lastincoming,
                'message': _('Missed call from {caller}')
            })\
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

        return callstate_item

    def _connect_channel_with_phonebook(self,
                                        callmonitor: CallMonitor,
                                        callstate_item: String,
                                        configuration: Configuration) -> None:
        if configuration.equipment.has_bridge('tr064'):
            phonebook_bridge = configuration.equipment.bridge('tr064')
            if phonebook_bridge.thing.has_property('phonebookInterval'):
                phonebook = phonebook_bridge.thing.channelprefix.replace(
                    ':', '_3A')
                String(callmonitor.item_ids.incoming_resolved)\
                    .label(_('Incoming call name'))\
                    .equipment(callmonitor)\
                    .semantic(PointType.STATUS)\
                    .channel(callmonitor.points.channel('incoming'), ProfileType.PHONEBOOK, {
                        'phonebook': phonebook,
                        'phoneNumberIndex': '1',
                        'matchCount': '5'
                    })\
                    .append_to(self)

                callstate_item.scripting(
                    {'resolved_item': callmonitor.item_ids.incoming_resolved})
