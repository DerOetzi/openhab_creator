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
    from openhab_creator.models.grafana import Dashboard


@SitemapCreatorPipeline(statuspage=3)
class BatterySitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('battery', False)

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        """No mainpage for batteries"""

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        page = Page('LowBattery')\
            .valuecolor(*self._valuecolors_low)\
            .append_to(statuspage)

        locations = []

        for battery in configuration.equipment.equipment('battery', False):
            location = battery.location.toplevel
            locations.append(location.identifier)
            frame = page.frame(location.identifier, location.name)

            if battery.points.has_battery_level:
                level = Text(battery.item_ids.levelbattery, battery.name_with_type)\
                    .valuecolor(*self._valuecolors_level)\
                    .append_to(frame)

            if battery.points.has_battery_low:
                low = Text(battery.item_ids.lowbattery, battery.name_with_type)\
                    .valuecolor(*self._valuecolors_low)\
                    .append_to(frame)

            if battery.points.has_battery_level and battery.points.has_battery_low:
                level.visibility((battery.item_ids.lowbattery, '==', 'OFF'))
                low.visibility((battery.item_ids.lowbattery, '!=', 'OFF'))

        self._add_grafana(configuration.dashboard, page,
                          list(dict.fromkeys(locations)),
                          _('Batteries status') + ' ')

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for batteries"""

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
