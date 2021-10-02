from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import (AISensorDataType, DateTime, Group,
                                          Number, NumberType, PointType,
                                          PropertyType, String)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.astro import \
        Astro


@ItemsCreatorPipeline(7)
class AstroItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('sunposition')\
            .append_to(self)

        Group('moonposition')\
            .append_to(self)

        for astro in configuration.equipment.equipment('astro'):
            Group(astro.item_ids.astro)\
                .label(astro.name)\
                .location(astro.location)\
                .semantic(astro)\
                .append_to(self)

            self.build_position(astro)
            self.build_rise_and_set(astro)
            self.build_eclipse(astro)
            self.build_moonphases(astro)

        self.write_file('astro')

    def build_position(self, astro: Astro):
        if astro.points.has_azimuth:
            Number(astro.item_ids.azimuth)\
                .label(_('Azimuth'))\
                .format('%.1f °')\
                .typed(NumberType.ANGLE)\
                .icon('astroposition')\
                .equipment(astro)\
                .groups(f'{astro.thing.typed}position')\
                .semantic(PointType.STATUS)\
                .sensor('astro', astro.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .channel(astro.points.channel('azimuth'))\
                .append_to(self)

        if astro.points.has_elevation:
            Number(astro.item_ids.elevation)\
                .label(_('Elevation'))\
                .format('%.1f °')\
                .typed(NumberType.ANGLE)\
                .icon('astroposition')\
                .equipment(astro)\
                .groups(f'{astro.thing.typed}position')\
                .semantic(PointType.STATUS)\
                .sensor('astro', astro.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .channel(astro.points.channel('elevation'))\
                .append_to(self)

    def build_rise_and_set(self, astro: Astro):
        if astro.points.has_rise:
            DateTime(astro.item_ids.rise)\
                .label(_('Rise'))\
                .timeonly()\
                .icon(f'{astro.thing.typed}rise')\
                .equipment(astro)\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .channel(astro.points.channel('rise'))\
                .append_to(self)

        if astro.points.has_set:
            DateTime(astro.item_ids.set)\
                .label(_('Set'))\
                .timeonly()\
                .icon(f'{astro.thing.typed}set')\
                .equipment(astro)\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .channel(astro.points.channel('set'))\
                .append_to(self)

    def build_eclipse(self, astro: Astro):
        if astro.points.has_eclipse_total:
            DateTime(astro.item_ids.eclipse_total)\
                .label(_('Total eclipse'))\
                .datetime()\
                .icon('eclipse')\
                .equipment(astro)\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .channel(astro.points.channel('eclipse_total'))\
                .append_to(self)

        if astro.points.has_eclipse_partial:
            DateTime(astro.item_ids.eclipse_partial)\
                .label(_('Partial eclipse'))\
                .datetime()\
                .icon('eclipse')\
                .equipment(astro)\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .channel(astro.points.channel('eclipse_partial'))\
                .append_to(self)

    def build_moonphases(self, astro: Astro) -> None:
        if astro.points.has_full:
            DateTime(astro.item_ids.full)\
                .label(_('Full moon'))\
                .dateonly_weekday()\
                .icon('moonfull')\
                .equipment(astro)\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .channel(astro.points.channel('full'))\
                .append_to(self)

        if astro.points.has_phase:
            String(astro.item_ids.phase)\
                .label(_('Moon phase'))\
                .icon('moon')\
                .equipment(astro)\
                .semantic(PointType.STATUS)\
                .channel(astro.points.channel('phase'))\
                .append_to(self)
