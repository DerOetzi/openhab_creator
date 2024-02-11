from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional
from abc import abstractmethod

from openhab_creator import _

from openhab_creator.models.sitemap import Image, Selection
from openhab_creator.models.grafana import Period, AggregateWindow

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.location import Location
    from openhab_creator.models.sitemap import Sitemap,  Frame, Page
    from openhab_creator.models.grafana import Dashboard


class BaseSitemapCreator():
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
                     prefix: Optional[str] = '',
                     aggregations: Optional[Dict[Period, AggregateWindow]] = None) -> None:
        grafana_urls = []
        for identifier in identifiers:
            panel_urls = dashboard.panel_urls(
                f'{prefix}{identifier}'.strip(),
                aggregations=aggregations)
            if panel_urls is not None:
                grafana_urls.append(panel_urls)

        if len(grafana_urls) > 0:
            frame = page.frame('period', _('Course'))
            mappings = []

            for period in Period:
                mappings.append((f'"{period}_actual"', period.label))
                mappings.append((f'"{period}_last"', period.last_label))

            Selection('guiPeriod', mappings)\
                .append_to(frame)

            self._graph_frame(grafana_urls, frame=frame)

    def _add_grafana_to_location_frames(self,
                                        dashboard: Dashboard,
                                        page: Page,
                                        locations: Dict[Location, Frame],
                                        prefix: Optional[str] = '',
                                        aggregations: Optional[Dict[Period, AggregateWindow]] = None) -> None:

        has_grafana = False

        for location, frame in locations.items():
            grafana_urls = []
            panel_urls = dashboard.panel_urls(
                f'{prefix}{location.name}'.strip(),
                aggregations=aggregations)
            if panel_urls is not None:
                grafana_urls.append(panel_urls)

            if len(grafana_urls) > 0:
                has_grafana = True
                self._graph_frame(grafana_urls, frame)

        if has_grafana:
            mappings = []

            for period in Period:
                mappings.append((f'"{period}_actual"', period.label))
                mappings.append((f'"{period}_last"', period.last_label))

            Selection('guiPeriod', mappings)\
                .append_to(page)

    @staticmethod
    def _graph_frame(grafana_urls: List[Dict[str, str]],
                     frame: Frame) -> None:
        for panel_urls in grafana_urls:
            for period in Period:
                if period in panel_urls:
                    Image(panel_urls[period][0])\
                        .visibility(('guiPeriod', '==', f'{period}_actual'))\
                        .append_to(frame)
                    
                    Image(panel_urls[period][1])\
                        .visibility(('guiPeriod', '==', f'{period}_last'))\
                        .append_to(frame)
