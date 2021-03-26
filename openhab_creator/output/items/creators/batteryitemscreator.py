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


@ItemsCreatorPipeline(10)
class BatteryItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        if configuration.has_equipment('battery', False):
            for equipment in configuration.equipment('battery', False):
                if equipment.category == 'sensor':
                    equipment_id = equipment.merged_sensor_id
                else:
                    equipment_id = equipment.equipment_id

                Group(equipment.battery_id)\
                    .label(_('Battery'))\
                    .groups(equipment_id)\
                    .tags('Battery')\
                    .append_to(self)

                if equipment.has_battery_low:
                    Switch(equipment.lowbattery_id)\
                        .label(_('Battery low'))\
                        .map(MapTransformation.LOWBATTERY)\
                        .icon('lowbattery')\
                        .groups('LowBattery', equipment.battery_id)\
                        .channel(equipment.channel('battery_low'))\
                        .semantic(PointType.LOWBATTERY)\
                        .append_to(self)

                if equipment.has_battery_level:
                    Number(equipment.levelbattery_id)\
                        .label(_('Battery level'))\
                        .percentage()\
                        .icon('battery')\
                        .groups(equipment.battery_id)\
                        .sensor('batteries', equipment.influxdb_tags)\
                        .channel(equipment.channel('battery_level'))\
                        .semantic(PointType.MEASUREMENT, PropertyType.LEVEL)\
                        .append_to(self)

            self.write_file('battery')
