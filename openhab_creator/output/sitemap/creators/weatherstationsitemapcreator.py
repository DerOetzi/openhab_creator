from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator.models.sitemap import Page, Text, Sitemap
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.grafana import Dashboard


@SitemapCreatorPipeline(mainpage=1)
class WeatherStationSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('weatherstation', False)

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        weatherstation = Page('weatherstation')\
            .append_to(sitemap)

        for condition in configuration.equipment.equipment('condition_id'):
            Text(condition.item_ids.condition)\
                .append_to(weatherstation)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No status page for weatherstation"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for weatherstation"""
