from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Tuple

from openhab_creator import _
from openhab_creator.models.sitemap import Page, Sitemap, Text
from openhab_creator.output.color import Color
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator
from openhab_creator.models.configuration.equipment.types.weatherstation import WeatherStationType

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment
    from openhab_creator.models.configuration.equipment.types.astro import \
        Astro
    from openhab_creator.models.configuration.equipment.types.weatherstation import \
        WeatherStation
    from openhab_creator.models.grafana import Dashboard


@SitemapCreatorPipeline(mainpage=1)
class WeatherStationSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('weatherstation', False)

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        weatherstation = Page('weatherstation')

        for condition in configuration.equipment.equipment('condition_id'):
            Text(condition.item_ids.condition)\
                .append_to(weatherstation)

        self._build_warnings(weatherstation, configuration)
        self._build_temperatures(weatherstation, configuration)
        self._build_rain_gauge(weatherstation, configuration)
        self._build_pressure(weatherstation, configuration)
        self._build_humidity(weatherstation, configuration)
        self._build_uvindex(weatherstation, configuration)
        self._build_ozone(weatherstation, configuration)

        self._build_astropage(weatherstation, configuration)

        weatherstation.append_to(sitemap)

    def _build_warnings(self, weatherstation_page: Page, configuration: Configuration) -> None:
        warnings = self.filter_stations(
            lambda x: x.points.has_warning_active, configuration)

        for station in warnings:
            Text(station.item_ids.warning_event_mapped)\
                .visibility((station.item_ids.warning_active, '!=', 'ON'))\
                .valuecolor(*self.warning_severity_valuecolors(station))\
                .append_to(weatherstation_page)

            weatherstation_page.valuecolor(
                *self.warning_severity_valuecolors(station))

            page = Page(station.item_ids.warning_event_mapped)\
                .visibility((station.item_ids.warning_active, '==', 'ON'))\
                .valuecolor(*self.warning_severity_valuecolors(station))\
                .append_to(weatherstation_page)

            Text(station.item_ids.warning_event_mapped)\
                .valuecolor(*self.warning_severity_valuecolors(station))\
                .append_to(page)

            Text(station.item_ids.warning_from)\
                .append_to(page)

            Text(station.item_ids.warning_to)\
                .visibility((station.item_ids.warning_to, '!=', 'NULL'))\
                .append_to(page)

    @staticmethod
    def warning_severity_valuecolors(station: WeatherStation) -> List[Tuple[str, Color]]:
        item = station.item_ids.warning_severity
        return [
            (f'{item}==Extreme', Color.VIOLETT),
            (f'{item}==Severe', Color.RED),
            (f'{item}==Moderate', Color.ORANGE),
            (f'{item}==Minor', Color.YELLOW),
            (f'{item}==NULL', Color.GREEN),
        ]

    def _build_temperatures(self, weatherstation_page: Page, configuration: Configuration) -> None:
        temperatures = self.filter_stations(lambda x: x.points.has_temperature,
                                            configuration)

        page = Page('temperatureOutdoor')\
            .label(_('Temperatures'))\
            .valuecolor(*self.temperature_valuecolors('temperatureOutdoor'))\
            .append_to(weatherstation_page)

        locations = []

        for temperature in temperatures:
            locations.append(temperature.location.toplevel)
            Text(temperature.item_ids.temperature)\
                .valuecolor(*self.temperature_valuecolors(temperature.item_ids.temperature))\
                .append_to(page)

            Text(f'trend{temperature.item_ids.temperature}')\
                .append_to(page)

            if temperature.points.has_humidex:
                Text(temperature.item_ids.humidex)\
                    .valuecolor(*self.temperature_valuecolors(temperature.item_ids.humidex))\
                    .append_to(page)

        if len(locations) > 0:
            self._add_grafana(configuration.dashboard, page,
                              list(dict.fromkeys(locations)),
                              _('Temperatures') + ' ')

    @staticmethod
    def temperature_valuecolors(item: str) -> List[Tuple[str, Color]]:
        return [
            (f'{item}>=28', Color.RED),
            (f'{item}>=24', Color.ORANGE),
            (f'{item}>=20', Color.YELLOW),
            (f'{item}>-30', Color.BLUE),
        ]

    def _build_rain_gauge(self, weatherstation_page: Page, configuration: Configuration) -> None:
        rain_gauges = self.filter_stations(
            lambda x: x.points.has_rain_gauge, configuration)

        page = Page('rain_gaugeWeatherStation')\
            .append_to(weatherstation_page)

        locations = []

        for rain_gauge in rain_gauges:
            locations.append(rain_gauge.location.toplevel)
            Text(rain_gauge.item_ids.rain_gauge)\
                .append_to(page)

        if len(locations) > 0:
            self._add_grafana(configuration.dashboard, page,
                              list(dict.fromkeys(locations)),
                              _('Rain gauge') + ' ')

    def _build_pressure(self, weatherstation_page: Page, configuration: Configuration) -> None:
        pressures = configuration.equipment.equipment('pressure')

        page = Page('pressureAll')\
            .append_to(weatherstation_page)

        locations = []

        for pressure in pressures:
            location = pressure.location.toplevel
            locations.append(location)
            frame = page.frame(
                location.identifier, location.name)
            if pressure.has_altitude:
                Text(pressure.item_ids.pressure_sealevel)\
                    .label(pressure.name)\
                    .append_to(frame)
            else:
                Text(pressure.item_ids.pressure)\
                    .label(pressure.name)\
                    .append_to(frame)

            Text(f'trend{pressure.item_ids.pressure}')\
                .label(_('Trend'))\
                .append_to(frame)

        if len(locations) > 0:
            self._add_grafana(configuration.dashboard, page,
                              list(dict.fromkeys(locations)),
                              _('Pressure') + ' ')

    def _build_humidity(self, weatherstation_page: Page, configuration: Configuration) -> None:
        humidities = self.filter_stations(lambda x: x.points.has_humidity,
                                          configuration)

        page = Page('humidityOutdoor')\
            .label(_('Humidity'))\
            .append_to(weatherstation_page)

        locations = []

        for humidity in humidities:
            location = humidity.location.toplevel
            locations.append(location)
            frame = page.frame(location.identifier, location.name)
            Text(humidity.item_ids.humidity)\
                .label(humidity.name)\
                .append_to(frame)

            Text(f'trend{humidity.item_ids.humidity}')\
                .label(_('Trend'))\
                .append_to(frame)

        if len(locations) > 0:
            self._add_grafana(configuration.dashboard, page,
                              list(dict.fromkeys(locations)),
                              _('Humidity') + ' ')

    def _build_uvindex(self, weatherstation_page: Page, configuration: Configuration) -> None:
        uvindexs = self.filter_stations(lambda x: x.points.has_uvindex,
                                        configuration)

        colors = WeatherStationType.UVINDEX.colors.outdoor_colors(  # pylint: disable=no-member
            'uvindexWeatherStation')

        page = Page('uvindexWeatherStation')\
            .label(_('UV index'))\
            .valuecolor(*colors)\
            .append_to(weatherstation_page)

        for uvindex in uvindexs:
            colors = WeatherStationType.UVINDEX.colors.outdoor_colors(  # pylint: disable=no-member
                uvindex.item_ids.uvindex)
            Text(uvindex.item_ids.uvindex)\
                .label(uvindex.name)\
                .valuecolor(*colors)\
                .append_to(page)

            frame = page\
                .frame(uvindex.identifier,
                       _('Self-protection time (below 3 hours) - {name}')
                       .format(name=uvindex.name))\
                .visibility((uvindex.item_ids.safeexposure(1), '<=', 180))

            for index in range(1, 7):
                Text(uvindex.item_ids.safeexposure(index))\
                    .visibility((uvindex.item_ids.safeexposure(index), '<=', 180))\
                    .append_to(frame)

    def _build_ozone(self, weatherstation_page: Page, configuration: Configuration) -> None:
        ozones = self.filter_stations(lambda x: x.points.has_ozone,
                                      configuration)

        colors = WeatherStationType.OZONE.colors.outdoor_colors(  # pylint: disable=no-member
            'ozoneWeatherStation')

        page = Page('guiozoneWeatherStation')\
            .label(_('Ozone'))\
            .valuecolor(*colors)\
            .append_to(weatherstation_page)

        for ozone in ozones:
            colors = WeatherStationType.OZONE.colors.outdoor_colors(  # pylint: disable=no-member
                ozone.item_ids.ozone)
            Text(ozone.item_ids.gui_ozone)\
                .label(ozone.name)\
                .valuecolor(*colors)\
                .append_to(page)

    @staticmethod
    def filter_stations(filter_func: Callable, configuration: Configuration) -> List[Equipment]:
        return list(filter(filter_func, configuration.equipment.equipment('weatherstation')))

    def _build_astropage(self, weatherstation_page: Page, configuration: Configuration) -> None:
        suns = configuration.equipment.equipment('sun')
        moons = configuration.equipment.equipment('moon')

        if len(suns) > 0 or len(moons) > 0:
            page = Page(label=_('Astro'))\
                .icon('astroposition')\
                .append_to(weatherstation_page)

            for sun in suns:
                self._build_sun(sun, page)

            for moon in moons:
                self._build_moon(moon, page)

    @staticmethod
    def _build_sun(sun: Astro, page: Page) -> None:
        frame = page.frame(sun.blankname)

        if sun.points.has_rise:
            Text(sun.item_ids.rise)\
                .label(_('Sun rise'))\
                .append_to(frame)

        if sun.points.has_set:
            Text(sun.item_ids.set)\
                .label(_('Sun set'))\
                .append_to(frame)

        if sun.points.has_azimuth:
            Text(sun.item_ids.azimuth)\
                .append_to(frame)

        if sun.points.has_elevation:
            Text(sun.item_ids.elevation)\
                .append_to(frame)

        if sun.points.has_eclipse_partial:
            Text(sun.item_ids.eclipse_partial)\
                .append_to(frame)

        if sun.points.has_eclipse_total:
            Text(sun.item_ids.eclipse_total)\
                .append_to(frame)

    @staticmethod
    def _build_moon(moon: Astro, page: Page) -> None:
        frame = page.frame(moon.blankname)

        if moon.points.has_rise:
            Text(moon.item_ids.rise)\
                .label(_('Moon rise'))\
                .append_to(frame)

        if moon.points.has_set:
            Text(moon.item_ids.set)\
                .label(_('Moon set'))\
                .append_to(frame)

        if moon.points.has_phase:
            Text(moon.item_ids.phase)\
                .append_to(frame)

        if moon.points.has_full:
            Text(moon.item_ids.full)\
                .append_to(frame)

        if moon.points.has_azimuth:
            Text(moon.item_ids.azimuth)\
                .append_to(frame)

        if moon.points.has_elevation:
            Text(moon.item_ids.elevation)\
                .append_to(frame)

        if moon.points.has_eclipse_partial:
            Text(moon.item_ids.eclipse_partial)\
                .append_to(frame)

        if moon.points.has_eclipse_total:
            Text(moon.item_ids.eclipse_total)\
                .append_to(frame)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No status page for weatherstation"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for weatherstation"""
