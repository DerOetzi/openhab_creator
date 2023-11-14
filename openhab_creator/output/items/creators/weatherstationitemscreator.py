from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.common.weatherstation import (DWDEvent,
                                                          WeatherCondition)
from openhab_creator.models.configuration.equipment.types.weatherstation import \
    WeatherStationType
from openhab_creator.models.items import (AISensorDataType, DateTime, Group, GroupType, Number,
                                          NumberType, PointType, ProfileType,
                                          String, Switch)
from openhab_creator.output.formatter import Formatter
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.weatherstation import \
        WeatherStation


@ItemsCreatorPipeline(11)
class WeatherStationItemsCreator(BaseItemsCreator):
    FITZPATRICK_LABELS = [
        _('Fitzpatrick skin type I'),
        _('Fitzpatrick skin type II'),
        _('Fitzpatrick skin type III'),
        _('Fitzpatrick skin type IV'),
        _('Fitzpatrick skin type V'),
        _('Fitzpatrick skin type VI')
    ]

    def __init__(self, outputdir: str):
        super().__init__(outputdir)
        self.groups = {}

    def build(self, configuration: Configuration) -> None:
        String('weatherstation')\
            .label(_('Weather station'))\
            .format('%s')\
            .scripting({
                'label': _('Weather station')
            })\
            .append_to(self)

        Group('WeatherCondition')\
            .append_to(self)

        Group('UVIndex')\
            .append_to(self)

        Group('WeatherWarning')\
            .append_to(self)

        Group('WeatherWarningSeverity')\
            .append_to(self)

        Group('WeatherWarningUrgency')\
            .append_to(self)

        Group('WeatherWarningEvent')\
            .append_to(self)

        Group('WeatherWarningEventMapped')\
            .append_to(self)

        Group('WeatherWarningFrom')\
            .append_to(self)

        Group('WeatherWarningTo')\
            .append_to(self)

        warning_stations = False

        for station in configuration.equipment.equipment('weatherstation'):
            self._build_station(station)

            if station.points.has_warning_active:
                self._build_warning(station)
                warning_stations = True

        if warning_stations:
            self._build_warning_configuration()

        self.write_file('weather')

    def _build_station(self, station: WeatherStation) -> None:
        if station.points.has_condition_id:
            Number(station.item_ids.condition)\
                .typed(NumberType.DIMENSIONLESS)\
                .label(_('Weather condition'))\
                .map(MapTransformation.WEATHERCONDITION)\
                .icon('weather')\
                .groups(station.item_ids.merged_sensor, 'WeatherCondition')\
                .semantic(PointType.STATUS)\
                .aisensor(AISensorDataType.CATEGORICAL)\
                .channel(station.points.channel('condition_id'),
                         ProfileType.SCALE, 'weathercondition.scale')\
                .scripting({
                    'icons': Formatter.key_value_tuples(WeatherCondition.mapping_icons,
                                                        separator=',')
                })\
                .append_to(self)

        for weathertype in WeatherStationType:
            if station.points.has(weathertype.point):
                sensor_item = self._build_station_weathertype(
                    weathertype, station)

                if weathertype == WeatherStationType.UVINDEX:
                    self._build_uvindex(station, sensor_item)

    def _build_station_weathertype(self,
                                   weathertype: WeatherStationType,
                                   station: WeatherStation) -> Number:
        if weathertype not in self.groups:
            group_item = Group(f'{weathertype}WeatherStation')\
                .typed(GroupType.NUMBER_AVG)\
                .label(weathertype.labels.page)\
                .format(weathertype.labels.format_str)\
                .icon(f'{weathertype}')\
                .append_to(self)
            
            if weathertype.typed.unit:
                group_item.unit(weathertype.typed.unit)

            if weathertype.labels.has_gui_factor:
                Group(f'gui{weathertype}WeatherStation')\
                    .typed(GroupType.NUMBER_AVG)\
                    .label(weathertype.labels.page)\
                    .transform_js(f'gui{weathertype}')\
                    .icon(f'{weathertype}')\
                    .append_to(self)

            self.groups[weathertype] = True

        sensor_item = Number(f'{weathertype}{station.identifier}')\
            .typed(weathertype.typed.number)\
            .label(weathertype.labels.item)\
            .format(weathertype.labels.format_str)\
            .icon(f'{weathertype}')\
            .groups(station.item_ids.merged_sensor, f'{weathertype}WeatherStation')\
            .semantic(PointType.MEASUREMENT, weathertype.typed.property)\
            .channel(station.points.channel(weathertype.point))\
            .sensor(weathertype.point, station.influxdb_tags)\
            .aisensor(AISensorDataType.NUMERICAL)\
            .append_to(self)
        
        if weathertype.typed.unit:
            sensor_item.unit(weathertype.typed.unit)

        if weathertype.labels.has_gui_factor:
            Number(f'gui{weathertype}{station.identifier}')\
                .typed(weathertype.typed.number)\
                .label(weathertype.labels.item)\
                .transform_js(f'gui{weathertype}')\
                .icon(f'{weathertype}')\
                .groups(station.item_ids.merged_sensor, f'gui{weathertype}WeatherStation')\
                .semantic(PointType.MEASUREMENT, weathertype.typed.property)\
                .channel(station.points.channel(weathertype.point),
                         ProfileType.JS, f'togui{weathertype.labels.gui_factor}.js')\
                .append_to(self)

        return sensor_item

    def _build_uvindex(self, station: WeatherStation, uvindex_item: Number) -> None:
        exposure_calcs = {}

        for index in range(1, 7):
            safeexposure_item = Number(station.item_ids.safeexposure(index))\
                .typed(NumberType.TIME)\
                .label(self.FITZPATRICK_LABELS[index-1])\
                .format('%d min')\
                .icon('safeexposure')\
                .groups(station.item_ids.merged_sensor)\
                .semantic(PointType.MEASUREMENT)\
                .append_to(self)

            if station.points.has(f'safeexposure{index}'):
                safeexposure_item.channel(
                    station.points.channel(f'safeexposure{index}'))
            else:
                exposure_calcs[f'safe{index}'] = station.item_ids.safeexposure(
                    index)

        uvindex_item\
            .groups('UVIndex')\
            .scripting(exposure_calcs)

    def _build_warning(self, station: WeatherStation) -> None:
        weatheritems = {}

        String(station.item_ids.warning_severity)\
            .label(_('Warning severity'))\
            .map(MapTransformation.DWDSEVERITY)\
            .channel(station.points.channel('warning_severity'))\
            .equipment(station)\
            .groups('WeatherWarningSeverity')\
            .semantic(PointType.STATUS)\
            .aisensor(AISensorDataType.CATEGORICAL)\
            .append_to(self)

        weatheritems['severity'] = station.item_ids.warning_severity

        if station.points.has_warning_headline:
            String(station.item_ids.warning_headline)\
                .label(_('Headline'))\
                .format('%s')\
                .channel(station.points.channel('warning_headline'))\
                .equipment(station)\
                .semantic(PointType.STATUS)\
                .append_to(self)

            weatheritems['headline'] = station.item_ids.warning_headline

        if station.points.has_warning_description:
            String(station.item_ids.warning_description)\
                .label(_('Description'))\
                .format('%s')\
                .channel(station.points.channel('warning_description'))\
                .equipment(station)\
                .semantic(PointType.STATUS)\
                .append_to(self)

            weatheritems['description'] = station.item_ids.warning_description

        Switch(station.item_ids.warning_urgency)\
            .label(_('Urgency'))\
            .format('%s')\
            .equipment(station)\
            .groups('WeatherWarningUrgency')\
            .semantic(PointType.STATUS)\
            .aisensor(AISensorDataType.CATEGORICAL)\
            .append_to(self)

        weatheritems['urgency'] = station.item_ids.warning_urgency

        String(station.item_ids.warning_event)\
            .label(_('Event'))\
            .format('%s')\
            .channel(station.points.channel('warning_event'))\
            .equipment(station)\
            .groups('WeatherWarningEvent')\
            .semantic(PointType.STATUS)\
            .append_to(self)

        String(station.item_ids.warning_event_mapped)\
            .label(_('Warning for'))\
            .map(MapTransformation.DWDEVENT)\
            .icon('dwdevent')\
            .equipment(station)\
            .groups('WeatherWarningEventMapped')\
            .semantic(PointType.STATUS)\
            .aisensor(AISensorDataType.CATEGORICAL)\
            .append_to(self)

        weatheritems['text'] = _('{} of {}')
        weatheritems['event'] = station.item_ids.warning_event
        weatheritems['event_mapped'] = station.item_ids.warning_event_mapped

        String(station.item_ids.warning_instruction)\
            .label(_('Instruction'))\
            .format('%s')\
            .channel(station.points.channel('warning_instruction'))\
            .equipment(station)\
            .semantic(PointType.STATUS)\
            .append_to(self)

        weatheritems['instruction'] = station.item_ids.warning_instruction

        DateTime(station.item_ids.warning_from)\
            .label(_('Valid from'))\
            .datetime()\
            .icon('clock')\
            .channel(station.points.channel('warning_from'))\
            .equipment(station)\
            .semantic(PointType.STATUS)\
            .scripting({'text': _('Valid from:')})\
            .append_to(self)

        weatheritems['from'] = station.item_ids.warning_from

        DateTime(station.item_ids.warning_to)\
            .label(_('Valid to'))\
            .datetime()\
            .icon('clock')\
            .channel(station.points.channel('warning_to'))\
            .equipment(station)\
            .semantic(PointType.STATUS)\
            .scripting({'text': _('Valid to:')})\
            .append_to(self)

        weatheritems['to'] = station.item_ids.warning_to

        weatheritems['icons'] = Formatter.key_value_tuples(
            DWDEvent.mapping_icons, separator=',')

        Switch(station.item_ids.warning_active)\
            .label(_('Warning'))\
            .map(MapTransformation.ACTIVE)\
            .channel(station.points.channel('warning_active'))\
            .equipment(station)\
            .groups('WeatherWarning')\
            .semantic(PointType.ALARM)\
            .aisensor(AISensorDataType.CATEGORICAL)\
            .scripting(weatheritems)\
            .append_to(self)

    def _build_warning_configuration(self) -> None:
        Switch('weatherwarningMinorActive')\
            .label(_('Minor warnings'))\
            .map(MapTransformation.ACTIVE)\
            .icon('notifications')\
            .config()\
            .append_to(self)

        Switch('weatherwarningModerateActive')\
            .label(_('Moderate warnings'))\
            .map(MapTransformation.ACTIVE)\
            .icon('notifications')\
            .config()\
            .append_to(self)

        Switch('weatherwarningSevereActive')\
            .label(_('Severe warnings'))\
            .map(MapTransformation.ACTIVE)\
            .icon('notifications')\
            .config()\
            .append_to(self)

        Switch('weatherwarningExtremeActive')\
            .label(_('Extreme warnings'))\
            .map(MapTransformation.ACTIVE)\
            .icon('notifications')\
            .config()\
            .append_to(self)
