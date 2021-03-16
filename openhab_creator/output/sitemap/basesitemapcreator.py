from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional
from abc import abstractmethod

from openhab_creator import _

from openhab_creator.models.sitemap import Switch, Image
from openhab_creator.models.grafana import Period

if TYPE_CHECKING:
    from openhab_creator.models.sitemap.baseelement import BaseElement
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.sitemap import Sitemap, Page, Frame
    from openhab_creator.models.grafana import Dashboard


class BaseSitemapCreator(object):
    @abstractmethod
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_mainpage")

    @abstractmethod
    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_statuspage")

    @abstractmethod
    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_configpage")

    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        #pylint: disable=unused-argument
        return True

    def _add_grafana(self,
                     dashboard: Dashboard,
                     page: Page,
                     identifiers: List[str],
                     prefix: Optional[str] = '') -> None:
        grafana_urls = []
        for identifier in identifiers:
            panel_urls = dashboard.panel_urls(f'{prefix}{identifier}')
            if panel_urls is not None:
                grafana_urls.append(panel_urls)

        self._graph_frame(page, grafana_urls)

    def _graph_frame(self, page: Page, grafana_urls: List[Dict[str, str]]) -> None:
        if len(grafana_urls) > 0:
            frame = page.frame('period', _('Course'))

            mappings = []

            for period in Period:
                mappings.append((f'"{period}"', period.label))

            Switch('guiPeriod', mappings)\
                .append_to(frame)

            for panel_urls in grafana_urls:
                Image(panel_urls[Period.DAY])\
                    .visibility(
                        ('guiPeriod', '==', Period.DAY),
                        ('guiPeriod', '==', 'Uninitialized')
                )\
                    .append_to(frame)

                Image(panel_urls[Period.WEEK])\
                    .visibility(('guiPeriod', '==', Period.WEEK))\
                    .append_to(frame)

                Image(panel_urls[Period.MONTH])\
                    .visibility(('guiPeriod', '==', Period.MONTH))\
                    .append_to(frame)

                Image(panel_urls[Period.YEAR])\
                    .visibility(('guiPeriod', '==', Period.YEAR))\
                    .append_to(frame)
