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


@SitemapCreatorPipeline(mainpage=0, statuspage=10)
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
        page = Page(label=_('White goods'))\
            .icon('whitegood')\
            .append_to(statuspage)

        for whitegood in configuration.equipment.equipment('whitegood'):
            device_page = Page(whitegood.item_ids.state)\
                .label(whitegood.blankname)\
                .append_to(page)

            Text(whitegood.item_ids.state)\
                .append_to(device_page)

            Text(whitegood.item_ids.power)\
                .append_to(device_page)

            if whitegood.has_reminder:
                Text(whitegood.item_ids.countdown)\
                    .visibility((whitegood.item_ids.done, '!=', 'OFF'))\
                    .append_to(device_page)

                Switch(whitegood.item_ids.done, [('ON', _('Done'))])\
                    .visibility((whitegood.item_ids.done, '!=', 'ON'))\
                    .append_to(device_page)

            Text(whitegood.item_ids.start)\
                .visibility((whitegood.item_ids.start, '!=', 'NULL'))\
                .append_to(device_page)

            self._add_grafana(configuration.dashboard, device_page,
                              ['', _('Average per hour')],
                              _('{whitegood} power').format(whitegood=whitegood.blankname) + ' ')

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for white goods"""
