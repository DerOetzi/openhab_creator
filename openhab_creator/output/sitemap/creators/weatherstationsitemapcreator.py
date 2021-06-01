from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

from openhab_creator import _
from openhab_creator.models.sitemap import Page, Text, Sitemap
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment
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

        self._build_temperatures(weatherstation, configuration)
        self._build_rain_gauge(weatherstation, configuration)

    def _build_temperatures(self, weatherstation_page: Page, configuration: Configuration) -> None:
        temperatures = self.filter_stations(lambda x: x.points.has_temperature,
                                            configuration)

        if len(temperatures) > 0:
            page = Page('temperatureOutdoor')\
                .label(_('Temperatures'))\
                .append_to(weatherstation_page)

            locations = []

            for temperature in temperatures:
                locations.append(temperature.location.toplevel)
                Text(temperature.item_ids.temperature)\
                    .append_to(page)

                if temperature.points.has_humidex:
                    Text(temperature.item_ids.humidex)\
                        .append_to(page)

            self._add_grafana(configuration.dashboard, page,
                              list(dict.fromkeys(locations)),
                              _('Temperatures') + ' ')

    def _build_rain_gauge(self, weatherstation_page: Page, configuration: Configuration) -> None:
        rain_gauges = self.filter_stations(
            lambda x: x.points.has_rain_gauge, configuration)

        if len(rain_gauges) > 0:
            page = Page('rain_gaugeWeatherStation')\
                .append_to(weatherstation_page)

            locations = []

            for rain_gauge in rain_gauges:
                locations.append(rain_gauge.location.toplevel)
                Text(rain_gauge.item_ids.rain_gauge)\
                    .append_to(page)

            self._add_grafana(configuration.dashboard, page,
                              list(dict.fromkeys(locations)),
                              _('Rain gauge') + ' ')

    @staticmethod
    def filter_stations(filter_func: Callable, configuration: Configuration) -> List[Equipment]:
        return list(filter(filter_func, configuration.equipment.equipment('weatherstation')))

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No status page for weatherstation"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for weatherstation"""
