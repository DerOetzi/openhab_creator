from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.equipment.types.gasstation import (
    FuelType, GasStation)
from openhab_creator.models.items import (Contact, Group, GroupType, Number,
                                          NumberType, PointType)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(8)
class GasStationItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        gasstations = configuration.equipment.equipment('gasstation')

        self._build_groups()

        for gasstation in gasstations:
            self._build_gasstation(gasstation)

        self.write_file('gasstation')

    def _build_groups(self) -> None:
        Group('FuelPrices')\
            .append_to(self)

        for fueltype in FuelType:
            Group(fueltype.group_identifier)\
                .typed(GroupType.NUMBER_MIN)\
                .label(fueltype.label)\
                .format('%.3f \\u20AC')\
                .groups('FuelPrices')\
                .append_to(self)

        Group('GasStationOpened')\
            .append_to(self)

    def _build_gasstation(self, gasstation: GasStation) -> None:
        Group(gasstation.item_ids.gasstation)\
            .label(gasstation.blankname)\
            .location(gasstation.location)\
            .semantic(gasstation)\
            .append_to(self)

        for fueltype in FuelType:
            if gasstation.points.has(fueltype.identifier):
                Number(gasstation.item_ids.price(fueltype))\
                    .typed(NumberType.DIMENSIONLESS)\
                    .label(fueltype.label)\
                    .format('%.3f \\u20AC')\
                    .icon(f'{fueltype}')\
                    .equipment(gasstation)\
                    .groups(fueltype.group_identifier)\
                    .semantic(PointType.STATUS)\
                    .sensor('fuelprice', {'typed': f'{fueltype}', **gasstation.influxdb_tags})\
                    .channel(gasstation.points.channel(f'{fueltype}'))\
                    .scripting({
                        'difference_item': gasstation.item_ids.difference(fueltype),
                        'opened_item': gasstation.item_ids.opened
                    })\
                    .append_to(self)

                Number(gasstation.item_ids.difference(fueltype))\
                    .typed(NumberType.DIMENSIONLESS)\
                    .append_to(self)

        Contact(gasstation.item_ids.opened)\
            .channel(gasstation.points.channel('opened'))\
            .label(_('Station status'))\
            .map(MapTransformation.STATION_OPEN)\
            .equipment(gasstation)\
            .groups('GasStationOpened')\
            .semantic(PointType.OPENSTATE)\
            .channel(gasstation.points.channel('opened'))\
            .append_to(self)
