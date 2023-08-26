from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.configuration import Configuration
from openhab_creator.models.configuration.equipment.types.pollencount import \
    PollenType
from openhab_creator.models.sitemap import Page, Sitemap, Text, Frame
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.pollencount import \
        PollenCount


@SitemapCreatorPipeline(mainpage=70)
class PollenCountSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('pollencount')

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        page = Page('pollenCountToday')\
            .append_to(sitemap)

        pollencounts = []

        for pollencount in configuration.equipment.equipment('pollencount'):
            self._build_pollencount(page, pollencount)
            pollencounts.append(pollencount.blankname)

        self._add_grafana(configuration.dashboard, page,
                          pollencounts, _('Pollen count index') + ' ')

    def _build_pollencount(self, page: Page, pollencount: PollenCount) -> None:
        frame = page.frame(pollencount.identifier, pollencount.blankname)

        for pollentype in PollenType:
            if pollencount.points.has_today(pollentype):
                self._build_pollentype(frame, pollentype, pollencount)

    def _build_pollentype(self, frame: Frame, pollentype: PollenType, pollencount: PollenCount) -> None:
        if pollencount.points.has_tomorrow(pollentype)\
                or pollencount.points.has_day_after_tomorrow(pollentype):
            subpage = Page(pollencount.item_ids.today(pollentype))\
                .append_to(frame)

            Text(pollencount.item_ids.today(pollentype))\
                .append_to(subpage)

            if pollencount.points.has_tomorrow(pollentype):
                Text(pollencount.item_ids.tomorrow(pollentype))\
                    .append_to(subpage)

            if pollencount.points.has_day_after_tomorrow(pollentype):
                Text(pollencount.item_ids.day_after_tomorrow(pollentype))\
                    .append_to(subpage)
        else:
            Text(pollencount.item_ids.today(pollentype))\
                .append_to(frame)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for indoor sensors"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for indoor sensors"""
