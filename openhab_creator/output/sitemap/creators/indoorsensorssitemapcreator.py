from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator.models.configuration import Configuration
from openhab_creator.models.configuration.equipment.types.sensor import \
    SensorType
from openhab_creator.models.sitemap import Frame, Page, Sitemap, Text
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.sensor import \
        Sensor


@SitemapCreatorPipeline(mainpage=5)
class IndoorSensorsSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        for sensortype in SensorType:
            if sensortype.point == "temperature":
                continue

            sensors = configuration.equipment(sensortype.point, False)
            sensors = list(filter(
                lambda x: x.location.area in ['Indoor', 'Building'], sensors))

            if len(sensors) > 0:
                sitemap.element(self.build_sensorpage(
                    configuration, sensortype, sensors))

    def build_sensorpage(self, configuration: Configuration,
                         sensortype: SensorType, sensors: List[Sensor]) -> Page:

        prefix = 'gui' if sensortype.labels.has_gui_factor else ''

        page = Page(f'{prefix}{sensortype}Indoor')
        locations = []

        if sensortype.colors.has_indoor:
            page.valuecolor(
                *sensortype.colors.indoor_colors(f'{sensortype}Indoor'))

        for sensor in sensors:
            if sensor.has_point(sensortype.point):
                location = sensor.toplevel_location
                locations.append(location)
                frame = page.frame(
                    location.identifier, location.name)

                sensor_text = Text(f'{prefix}{sensortype}{sensor.sensor_id}')\
                    .label(sensor.name)

                if sensortype.colors.has_indoor:
                    sensor_text.valuecolor(*sensortype.colors.indoor_colors(
                        f'{sensortype}{sensor.sensor_id}'))

                sensor_text.append_to(frame)

                if sensortype.point == 'moisture':
                    self.build_moisture(frame, sensor)

        self._add_grafana(configuration.dashboard, page,
                          list(dict.fromkeys(locations)),
                          f'{sensortype.labels.page} ')

        return page

    def build_moisture(self, frame: Frame, sensor: Sensor) -> None:
        Text(sensor.moisturelastwatered_id)\
            .append_to(frame)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for indoor sensors"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for indoor sensors"""