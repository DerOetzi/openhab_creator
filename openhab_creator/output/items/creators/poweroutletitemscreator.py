from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import (AISensorDataType, Group, Number, NumberType, PointType,
                                          PropertyType, Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(7)
class PowerOutletItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('PowerOutlet')\
            .append_to(self)

        for poweroutlet in configuration.equipment.equipment('poweroutlet'):
            poweroutlet_item = Group(poweroutlet.item_ids.poweroutlet)\
                .semantic('PowerOutlet')\
                .append_to(self)

            if poweroutlet.poweroutlet_is_subequipment:
                poweroutlet_item\
                    .label(_('Power outlet'))\
                    .equipment(poweroutlet)
            else:
                poweroutlet_item\
                    .label(poweroutlet.name_with_type)\
                    .location(poweroutlet.location)

            if poweroutlet.points.has_onoff:
                onoff_item = Switch(poweroutlet.item_ids.onoff)\
                    .label(_('On/Off'))\
                    .equipment(poweroutlet.item_ids.poweroutlet)\
                    .config()\
                    .semantic(PointType.SWITCH)\
                    .channel(poweroutlet.points.channel('onoff'))\
                    .scripting(poweroutlet.scripting)\
                    .append_to(self)

                if poweroutlet.onoff_group is not None:
                    onoff_item.groups(poweroutlet.onoff_group)

            if poweroutlet.points.has_power:
                Number(poweroutlet.item_ids.power)\
                    .typed(NumberType.POWER)\
                    .label(_('Power'))\
                    .format('%,.2f W')\
                    .icon('poweroutlet')\
                    .equipment(poweroutlet.item_ids.poweroutlet)\
                    .groups(poweroutlet.group)\
                    .sensor('power', poweroutlet.influxdb_tags)\
                    .aisensor(AISensorDataType.NUMERICAL)\
                    .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                    .channel(poweroutlet.points.channel('power'))\
                    .scripting(poweroutlet.scripting)\
                    .append_to(self)

        self.write_file('poweroutlet')
