from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import (
    AISensorDataType, Group, Number, PointType, PropertyType)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.smartmeter import SmartMeter


@ItemsCreatorPipeline(5)
class SmartMeterItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        for smartmeter in configuration.equipment.equipment('smartmeter'):
            self.build_smartmeter(smartmeter)
            self.build_consumption(smartmeter)

        self.write_file('smartmeter')

    def build_smartmeter(self, smartmeter: SmartMeter) -> None:
        Group(smartmeter.item_ids.smartmeter)\
            .label(smartmeter.blankname)\
            .location(smartmeter.location)\
            .icon('smartmeter')\
            .semantic(smartmeter)\
            .append_to(self)

    def build_consumption(self, smartmeter: SmartMeter) -> None:
        if smartmeter.points.has_consumed_total:
            Number(smartmeter.item_ids.consumed_total)\
                .consumption()\
                .label(_('Consumed total'))\
                .icon('energy')\
                .equipment(smartmeter)\
                .semantic(PointType.MEASUREMENT, PropertyType.ENERGY)\
                .sensor('smartmeter_consumed', smartmeter.influxdb_tags, add_item_label=True)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .channel(smartmeter.points.channel('consumed_total'))\
                .append_to(self)

        for tariff in [1, 2]:
            if smartmeter.points.has_consumed(tariff):
                Number(smartmeter.item_ids.consumed(tariff))\
                    .consumption()\
                    .label(_('Consumed tariff {tariff}').format(tariff=tariff))\
                    .icon('energy')\
                    .equipment(smartmeter)\
                    .semantic(PointType.MEASUREMENT, PropertyType.ENERGY)\
                    .sensor('smartmeter_consumed', smartmeter.influxdb_tags, add_item_label=True)\
                    .aisensor(AISensorDataType.NUMERICAL)\
                    .channel(smartmeter.points.channel(f'consumed_t{tariff}'))\
                    .append_to(self)
