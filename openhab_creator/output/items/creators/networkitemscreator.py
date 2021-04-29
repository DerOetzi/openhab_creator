from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import (Group, GroupType, PointType,
                                          PropertyType, Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.networkappliance import \
        NetworkAppliance


@ItemsCreatorPipeline(10)
class NetworkItemsCreator(BaseItemsCreator):
    def build(self, configuration) -> None:
        Group('Networkstatus')\
            .typed(GroupType.ONOFF)\
            .label(_('Network status'))\
            .map(MapTransformation.ONLINE)\
            .append_to(self)

        for lan in configuration.equipment('lan', False):
            self.build_equipment(lan)

        self.write_file('network')

    def build_equipment(self, lan: NetworkAppliance) -> None:
        for mac, equipment in lan.macs.items():
            online = Switch(equipment.maconline_id)\
                .label(_('Network status'))\
                .equipment(equipment)\
                .channel(lan.maconline_channel(mac))\
                .semantic(PointType.STATUS)

            if equipment.has_person:
                online.groups(equipment.person.presence_id)\
                    .map(MapTransformation.PRESENCE)\
                    .icon('presence')\
                    .semantic(PropertyType.PRESENCE)
            else:
                online.groups('Networkstatus')\
                    .map(MapTransformation.ONLINE)

            online.append_to(self)
