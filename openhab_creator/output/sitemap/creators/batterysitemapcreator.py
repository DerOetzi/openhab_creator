from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _, logger
from openhab_creator.models.sitemap import Page, Text
from openhab_creator.output.color import Color
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.grafana import Dashboard


@SitemapCreatorPipeline(statuspage=0)
class BatterySitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.has_equipment('battery')

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        page = Page('LowBattery')\
            .valuecolor(self._valuecolors_low)\
            .append_to(statuspage)

        locations = []

        for battery in configuration.equipment('battery'):
            location = battery.toplevel_location
            locations.append(location.identifier)
            frame = page.frame(location.identifier, location.name)

            if battery.has_battery_level:
                level = Text(battery.levelbattery_id, battery.name_with_type)\
                    .valuecolor(self._valuecolors_level)\
                    .append_to(frame)

            if battery.has_battery_low:
                low = Text(battery.lowbattery_id, battery.name_with_type)\
                    .valuecolor(self._valuecolors_low)\
                    .append_to(frame)

            if battery.has_battery_level and battery.has_battery_low:
                level.visibility([(battery.lowbattery_id, '==', 'OFF')])
                low.visibility([(battery.lowbattery_id, '!=', 'OFF')])

        self.add_grafana(configuration.dashboard, page,
                         list(dict.fromkeys(locations)))

    @property
    def _valuecolors_low(self) -> List[Color]:
        return [
            ('ON', Color.RED),
            ('1', Color.RED),
            ('OFF', Color.GREEN),
            ('0', Color.GREEN)
        ]

    @property
    def _valuecolors_level(self) -> List[Color]:
        return [
            ('>=60', Color.GREEN),
            ('>=30', Color.YELLOW),
            ('>=20', Color.ORANGE),
            ('>=0', Color.RED)
        ]

    def add_grafana(self,
                    dashboard: Dashboard,
                    page: Page,
                    locations: List[str]) -> None:
        grafana_urls = []
        for location in locations:
            panel_urls = dashboard.panel_urls(f'Batteries_{location}')
            if panel_urls is not None:
                grafana_urls.append(panel_urls)

        self._graph_frame(page, grafana_urls)
