from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import (Group, Number, PointType,
                                          PropertyType, Switch)
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
from openhab_creator.output.items import ItemsCreatorPipeline

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(20)
class BatteryItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        if configuration.equipment.has('battery', False):
            for equipment in configuration.equipment.equipment('battery', False):
                if equipment.category == 'sensor':
                    equipment_id = equipment.item_ids.merged_sensor
                else:
                    equipment_id = equipment.item_ids.equipment_id

                Group(equipment.item_ids.battery)\
                    .label(_('Battery'))\
                    .groups(equipment_id)\
                    .semantic('Battery')\
                    .append_to(self)

                if equipment.points.has_battery_low:
                    Switch(equipment.item_ids.lowbattery)\
                        .label(_('Battery low'))\
                        .map(MapTransformation.LOWBATTERY)\
                        .icon('lowbattery')\
                        .groups('LowBattery', equipment.item_ids.battery)\
                        .channel(equipment.points.channel('battery_low'))\
                        .semantic(PointType.LOWBATTERY)\
                        .append_to(self)

                if equipment.points.has_battery_level:
                    Number(equipment.item_ids.levelbattery)\
                        .label(_('Battery level'))\
                        .percentage()\
                        .icon('battery')\
                        .groups(equipment.item_ids.battery)\
                        .sensor('batteries', equipment.influxdb_tags)\
                        .channel(equipment.points.channel('battery_level'))\
                        .semantic(PointType.MEASUREMENT, PropertyType.LEVEL)\
                        .append_to(self)

            self.write_file('battery')
