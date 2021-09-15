from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.equipment.types.pollencount import \
    PollenType
from openhab_creator.models.items import (Group, GroupType, Number, NumberType,
                                          PointType, ProfileType)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.pollencount import \
        PollenCount


@ItemsCreatorPipeline(8)
class PollenCountItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        has_pollencount, pollencounts = configuration.equipment.has(
            'pollencount')

        if has_pollencount:
            Group('pollenCountToday')\
                .typed(GroupType.NUMBER_MAX)\
                .label(_('Pollen count index'))\
                .map(MapTransformation.POLLENCOUNT)\
                .icon('pollencount')\
                .append_to(self)

            for pollencount in pollencounts:
                self.build_pollencount(pollencount)

            self.write_file('pollencount')

    def build_pollencount(self, pollencount: PollenCount) -> None:
        Group(pollencount.item_ids.pollencount)\
            .label(_('Pollen count index {name}').format(name=pollencount.blankname))\
            .location(pollencount.location)\
            .semantic(pollencount)\
            .append_to(self)

        for pollentype in PollenType:
            if pollencount.points.has_today(pollentype):
                influxdb_tags = pollencount.influxdb_tags
                influxdb_tags['label'] = pollentype.label

                self._build_pollentype(pollentype, '{pollentype}', pollencount.item_ids.today(pollentype),
                                       pollencount.points.channel(f'{pollentype}_today'))\
                    .equipment(pollencount)\
                    .groups('pollenCountToday')\
                    .sensor('pollencountindex', influxdb_tags)

            if pollencount.points.has_tomorrow(pollentype):
                self._build_pollentype(pollentype, _(
                    '{pollentype} tomorrow'), pollencount.item_ids.tomorrow(pollentype),
                    pollencount.points.channel(f'{pollentype}_tomorrow'))\
                    .equipment(pollencount)

            if pollencount.points.has_day_after_tomorrow(pollentype):
                self._build_pollentype(pollentype, _(
                    '{pollentype} day after tomorrow'), pollencount.item_ids.day_after_tomorrow(pollentype),
                    pollencount.points.channel(f'{pollentype}_dayafter'))\
                    .equipment(pollencount)

    def _build_pollentype(self, pollentype: PollenType, label: str,
                          item: str, channel: str) -> Number:
        return Number(item)\
            .label(label.format(pollentype=pollentype.label))\
            .map(MapTransformation.POLLENCOUNT)\
            .icon('pollencount')\
            .typed(NumberType.DIMENSIONLESS)\
            .semantic(PointType.MEASUREMENT)\
            .channel(channel, ProfileType.MAP, 'pollencountapi.map')\
            .append_to(self)
