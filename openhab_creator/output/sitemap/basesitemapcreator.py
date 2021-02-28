from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from openhab_creator import _

from openhab_creator.models.sitemap import Switch, Image
from openhab_creator.models.grafana import Period

if TYPE_CHECKING:
    from openhab_creator.models.sitemap.baseelement import BaseElement
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.sitemap import Sitemap, Page, Frame


class BaseSitemapCreator(object):
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_mainpage")

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_statuspage")

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_configpage")

    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return True

    def _graph_frame(self, page: Page, grafana_urls: List[Dict[str, str]]) -> None:
        if len(grafana_urls) > 0:
            frame = page.frame('period', _('Course'))

            mappings = []

            for period_config in Period:
                period = period_config.value['period']
                name = period_config.value['name']
                mappings.append((period, name))

            Switch('guiPeriod', mappings)\
                .append_to(frame)

            for panel_urls in grafana_urls:
                Image(panel_urls[Period.DAY.value['period']])\
                    .append_to(frame)
