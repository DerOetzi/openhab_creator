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
            self.build_delivered(smartmeter)
            self.build_power(smartmeter)

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
                .energy()\
                .label(_('Consumed total'))\
                .icon('smartmeterconsumption')\
                .equipment(smartmeter)\
                .semantic(PointType.MEASUREMENT, PropertyType.ENERGY)\
                .sensor('smartmeter_consumed', smartmeter.influxdb_tags, add_item_label=True)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .channel(smartmeter.points.channel('consumed_total'))\
                .unit('kWh')\
                .append_to(self)

        for tariff in range(1, 3):
            if smartmeter.points.has_consumed(tariff):
                Number(smartmeter.item_ids.consumed(tariff))\
                    .energy()\
                    .label(_('Consumed tariff {tariff}').format(tariff=tariff))\
                    .icon('smartmeterconsumption')\
                    .equipment(smartmeter)\
                    .semantic(PointType.MEASUREMENT, PropertyType.ENERGY)\
                    .sensor('smartmeter_consumed', smartmeter.influxdb_tags, add_item_label=True)\
                    .aisensor(AISensorDataType.NUMERICAL)\
                    .channel(smartmeter.points.channel(f'consumed_t{tariff}'))\
                    .unit('kWh')\
                    .append_to(self)

    def build_delivered(self, smartmeter: SmartMeter) -> None:
        if smartmeter.points.has_delivered_total:
            Number(smartmeter.item_ids.delivered_total)\
                .energy()\
                .label(_('Delivered total'))\
                .icon('smartmeterdelivery')\
                .equipment(smartmeter)\
                .semantic(PointType.MEASUREMENT, PropertyType.ENERGY)\
                .sensor('smartmeter_delivered', smartmeter.influxdb_tags, add_item_label=True)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .channel(smartmeter.points.channel('delivered_total'))\
                .unit('kWh')\
                .append_to(self)

    def build_power(self, smartmeter: SmartMeter) -> None:
        if smartmeter.points.has_power_total:
            Number(smartmeter.item_ids.power_total)\
                .power()\
                .label(_('Power total'))\
                .icon('power')\
                .equipment(smartmeter)\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .sensor('smartmeter_power', smartmeter.influxdb_tags, add_item_label=True)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .channel(smartmeter.points.channel('power_total'))\
                .unit('W')\
                .append_to(self)

        for phase in range(1, 4):
            if smartmeter.points.has_power(phase):
                Number(smartmeter.item_ids.power(phase))\
                    .power()\
                    .label(_('Power phase {phase}').format(phase=phase))\
                    .icon('power')\
                    .equipment(smartmeter)\
                    .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                    .sensor('smartmeter_power', smartmeter.influxdb_tags, add_item_label=True)\
                    .aisensor(AISensorDataType.NUMERICAL)\
                    .channel(smartmeter.points.channel(f'power_p{phase}'))\
                    .unit('W')\
                    .append_to(self)
