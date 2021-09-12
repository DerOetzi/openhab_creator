from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.equipment.types.pollencount import \
    PollenType
from openhab_creator.models.items import (Group, GroupType, PointType,
                                          ProfileType, String)
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
                self._build_pollentype(pollentype, '{pollentype}', 'Today',
                                       pollencount.points.channel(f'{pollentype}_today'))\
                    .equipment(pollencount)\
                    .groups('pollenCountToday')\
                    .sensor('pollencountindex', pollencount.influxdb_tags)

            if pollencount.points.has_tomorrow(pollentype):
                self._build_pollentype(pollentype, _(
                    '{pollentype} tomorrow'), 'Tomorrow',
                    pollencount.points.channel(f'{pollentype}_tomorrow'))\
                    .equipment(pollencount)

            if pollencount.points.has_day_after_tomorrow(pollentype):
                self._build_pollentype(pollentype, _(
                    '{pollentype} day after tomorrow'), 'DayAfterTomorrow',
                    pollencount.points.channel(f'{pollentype}_dayafter'))\
                    .equipment(pollencount)

    def _build_pollentype(self, pollentype: PollenType, label: str,
                          item_suffix: str, channel: str) -> String:
        return String(f'pollenCount{pollentype}{item_suffix}')\
            .label(label.format(pollentype=pollentype.label))\
            .map(MapTransformation.POLLENCOUNT)\
            .semantic(PointType.MEASUREMENT)\
            .channel(channel, ProfileType.MAP, 'pollencountapi.map')\
            .append_to(self)
