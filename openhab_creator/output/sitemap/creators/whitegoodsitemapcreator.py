from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.sitemap import Page, Sitemap, Switch, Text
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.grafana import Dashboard


@SitemapCreatorPipeline(mainpage=0, statuspage=2)
class WhiteGoodSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('whitegood', False)

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        for whitegood in configuration.equipment.equipment('whitegood'):
            if whitegood.has_reminder:
                Switch(whitegood.item_ids.done, [('ON', _('Done'))])\
                    .visibility((whitegood.item_ids.done, '!=', 'ON'))\
                    .append_to(sitemap)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        for whitegood in configuration.equipment.equipment('whitegood'):
            page = Page(whitegood.item_ids.state)\
                .label(whitegood.blankname)\
                .append_to(statuspage)

            Text(whitegood.item_ids.state)\
                .append_to(page)

            Text(whitegood.item_ids.power)\
                .append_to(page)

            if whitegood.has_reminder:
                Text(whitegood.item_ids.countdown)\
                    .visibility((whitegood.item_ids.done, '!=', 'OFF'))\
                    .append_to(page)

                Switch(whitegood.item_ids.done, [('ON', _('Done'))])\
                    .visibility((whitegood.item_ids.done, '!=', 'ON'))\
                    .append_to(page)

            Text(whitegood.item_ids.start)\
                .visibility((whitegood.item_ids.start, '!=', 'NULL'))\
                .append_to(page)

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for white goods"""
