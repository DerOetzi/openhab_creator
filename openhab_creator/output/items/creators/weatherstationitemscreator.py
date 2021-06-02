from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.equipment.types.weatherstation import \
    WeatherStationType
from openhab_creator.models.items import (Group, GroupType, Number, PointType,
                                          ProfileType, String, Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.weatherstation import \
        WeatherStation


@ItemsCreatorPipeline(7)
class WeatherStationItemsCreator(BaseItemsCreator):
    def __init__(self, outputdir: str):
        super().__init__(outputdir)
        self.groups = {}

    def build(self, configuration: Configuration) -> None:
        String('weatherstation')\
            .label(_('Weather station'))\
            .append_to(self)

        Group('WeatherCondition')\
            .append_to(self)

        Group('WeatherWarning')\
            .append_to(self)

        for station in configuration.equipment.equipment('weatherstation'):
            self._build_station(station)

            if station.points.has_warning_active:
                self._build_warning(station)

        self.write_file('weather')

    def _build_station(self, station: WeatherStation) -> None:
        if station.points.has_condition_id:
            String(station.item_ids.condition)\
                .label(_('Weather condition'))\
                .map(MapTransformation.WEATHERCONDITION)\
                .icon('weather')\
                .groups(station.item_ids.merged_sensor, 'WeatherCondition')\
                .semantic(PointType.STATUS)\
                .channel(station.points.channel('condition_id'),
                         ProfileType.SCALE, 'weathercondition.scale')\
                .append_to(self)

        for weathertype in WeatherStationType:
            if station.points.has(weathertype.point):
                if weathertype not in self.groups:
                    Group(f'{weathertype}WeatherStation')\
                        .typed(GroupType.NUMBER_AVG)\
                        .label(weathertype.labels.page)\
                        .format(weathertype.labels.format_str)\
                        .icon(f'{weathertype}')\
                        .append_to(self)

                    self.groups[weathertype] = True

                Number(f'{weathertype}{station.identifier}')\
                    .typed(weathertype.typed.number)\
                    .label(weathertype.labels.item)\
                    .format(weathertype.labels.format_str)\
                    .icon(f'{weathertype}')\
                    .groups(station.item_ids.merged_sensor, f'{weathertype}WeatherStation')\
                    .semantic(PointType.MEASUREMENT, weathertype.typed.property)\
                    .channel(station.points.channel(weathertype.point))\
                    .sensor(weathertype.point, station.influxdb_tags)\
                    .aisensor()\
                    .append_to(self)

    def _build_warning(self, station: WeatherStation) -> None:
        weatheritems = {}

        String(station.item_ids.warning_severity)\
            .label(_('Warning severity'))\
            .map(MapTransformation.DWDSEVERITY)\
            .channel(station.points.channel('warning_severity'))\
            .equipment(station)\
            .semantic(PointType.STATUS)\
            .aisensor()\
            .append_to(self)

        weatheritems['severity'] = station.item_ids.warning_severity

        if station.points.has_warning_headline:
            String(station.item_ids.warning_headline)\
                .label(_('Headline'))\
                .format('%s')\
                .channel(station.points.channel('warning_headline'))\
                .equipment(station)\
                .semantic(PointType.STATUS)\
                .aisensor()\
                .append_to(self)

            weatheritems['headline'] = station.item_ids.warning_headline

        String(station.item_ids.warning_urgency)\
            .label(_('Urgency'))\
            .format('%s')\
            .channel(station.points.channel('warning_urgency'))\
            .equipment(station)\
            .semantic(PointType.STATUS)\
            .aisensor()\
            .append_to(self)

        weatheritems['urgency'] = station.item_ids.warning_urgency

        String(station.item_ids.warning_event)\
            .label(_('Event'))\
            .format('%s')\
            .channel(station.points.channel('warning_event'))\
            .equipment(station)\
            .semantic(PointType.STATUS)\
            .append_to(self)

        String(station.item_ids.warning_event_mapped)\
            .label(_('Warning for'))\
            .map(MapTransformation.DWDEVENT)\
            .icon('dwdevent')\
            .equipment(station)\
            .semantic(PointType.STATUS)\
            .aisensor()\
            .append_to(self)

        weatheritems['event'] = station.item_ids.warning_event
        weatheritems['event_mapped'] = station.item_ids.warning_event_mapped

        Switch(station.item_ids.warning_active)\
            .label(_('Warning'))\
            .map(MapTransformation.ACTIVE)\
            .channel(station.points.channel('warning_active'))\
            .equipment(station)\
            .groups('WeatherWarning')\
            .semantic(PointType.ALARM)\
            .aisensor()\
            .scripting(weatheritems)\
            .append_to(self)
