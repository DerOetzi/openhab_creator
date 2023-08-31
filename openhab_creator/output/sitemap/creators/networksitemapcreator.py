from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _
from openhab_creator.models.sitemap import Page, Text, Sitemap
from openhab_creator.output.color import Color
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@SitemapCreatorPipeline(statuspage=40)
class NetworkSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('lan', False)

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        """No mainpage for batteries"""

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        page = Page('Networkstatus')\
            .valuecolor(*self.valuecolors_online)\
            .append_to(statuspage)

        for lancontroller in configuration.equipment.equipment('lan', False):
            for networkdevice in lancontroller.macs.values():
                if not networkdevice.has_person:
                    if networkdevice.location:
                        location = networkdevice.location.toplevel
                        frame = page.frame(location.identifier, location.name)
                    else:
                        frame = page.frame('general', _('General'))

                    Text(networkdevice.item_ids.maconline)\
                        .label(networkdevice.name_with_type)\
                        .valuecolor(*self.valuecolors_online)\
                        .append_to(frame)

    @property
    def valuecolors_online(self) -> List[Color]:
        return [
            ('ON', Color.GREEN),
            ('1', Color.GREEN),
            ('OFF', Color.RED),
            ('0', Color.RED)
        ]

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for batteries"""
