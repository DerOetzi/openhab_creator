from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorType)
from openhab_creator.models.items import (AISensorDataType, DateTime, Group,
                                          GroupType, Number, PointType,
                                          ProfileType, PropertyType, String)
from openhab_creator.models.items.baseitem import BaseItem
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(9)
class SensorItemsCreator(BaseItemsCreator):
    def __init__(self, outputdir: str):
        super().__init__(outputdir)
        self.sensors = {}

    def build(self, configuration: Configuration) -> None:
        self._build_groups()

        for sensor in configuration.equipment.equipment('sensor'):
            location = sensor.location
            area = location.area

            if area not in self.sensors:
                self.sensors[area] = {}

            self.build_sensor(sensor)

            if sensor.has_subequipment:
                for subsensor in sensor.subequipment:
                    if sensor.category not in ('sensor', 'poweroutlet'):
                        self.build_sensor(subsensor)

                    self.build_sensortype_area(subsensor)
            else:
                self.build_sensortype_area(sensor)

        self.write_file('sensors')

    def _build_groups(self) -> None:
        Group('Trend')\
            .append_to(self)

        Group('Average7d')\
            .append_to(self)

        Group('PressureSealevel')\
            .append_to(self)

        for sensortype in SensorType:
            group_item = Group(f'{sensortype}All')\
                .typed(GroupType.NUMBER_AVG)\
                .label(sensortype.labels.page)\
                .format(sensortype.labels.format_str)\
                .icon(f'{sensortype}')\
                .append_to(self)

            if sensortype.typed.unit:
                group_item.unit(sensortype.typed.unit)

            if sensortype.labels.has_gui_factor:
                Group(f'gui{sensortype}All')\
                    .typed(GroupType.NUMBER_AVG)\
                    .label(sensortype.labels.item)\
                    .transform_js(f'gui{sensortype}')\
                    .icon(f'{sensortype}')\
                    .append_to(self)

    def build_sensor(self, sensor: Sensor) -> None:
        sensor_equipment = Group(sensor.item_ids.sensor)\
            .semantic('Sensor')

        if sensor.sensor_is_subequipment:
            sensor_equipment\
                .label(_('Sensor'))\
                .equipment(sensor)
        else:
            sensor_equipment\
                .label(sensor.name_with_type)\
                .location(sensor.location)

        sensor_equipment.append_to(self)

    def build_sensortype_area(self, sensor: Sensor) -> None:
        area = sensor.location.area

        for sensortype in SensorType:
            if sensortype.point in sensor.categories:
                if sensortype not in self.sensors[area]:
                    self.sensors[area][sensortype] = {}
                    group_item = Group(f'{sensortype}{area}')\
                        .typed(GroupType.NUMBER_AVG)\
                        .label(sensortype.labels.item)\
                        .format(sensortype.labels.format_str)\
                        .icon(f'{sensortype}{area.lower()}')\
                        .groups(f'{sensortype}All')\
                        .append_to(self)

                    if sensortype.typed.unit:
                        group_item.unit(sensortype.typed.unit)

                    if sensortype.labels.has_gui_factor:
                        Group(f'gui{sensortype}{area}')\
                            .typed(GroupType.NUMBER_AVG)\
                            .label(sensortype.labels.item)\
                            .transform_js(f'gui{sensortype}')\
                            .icon(f'{sensortype}{area.lower()}')\
                            .groups(f'gui{sensortype}All')\
                            .append_to(self)

                self.build_sensortype_location(sensortype, sensor)

    def build_sensortype_location(self, sensortype: SensorType, sensor: Sensor) -> None:
        location = sensor.location
        area = location.area

        if location not in self.sensors[area][sensortype]:
            self.sensors[area][sensortype][location] = True
            group_item = Group(f'{sensortype}{location}')\
                .typed(GroupType.NUMBER_AVG)\
                .label(sensortype.labels.item)\
                .format(sensortype.labels.format_str)\
                .icon(f'{sensortype}{area.lower()}')\
                .groups(f'{sensortype}{area}')\
                .location(location)\
                .semantic(PointType.MEASUREMENT, sensortype.typed.property)\
                .append_to(self)

            if sensortype.typed.unit:
                group_item.unit(sensortype.typed.unit)

            if sensortype.labels.has_gui_factor:
                Group(f'gui{sensortype}{location}')\
                    .typed(GroupType.NUMBER_AVG)\
                    .label(sensortype.labels.item)\
                    .transform_js(f'gui{sensortype}')\
                    .icon(f'{sensortype}{area.lower()}')\
                    .groups(f'gui{sensortype}{area}')\
                    .location(location)\
                    .semantic(PointType.MEASUREMENT, sensortype.typed.property)\
                    .append_to(self)

        sensor_item = Number(f'{sensortype}{sensor.item_ids.merged_sensor}')\
            .typed(sensortype.typed.number)\
            .label(sensortype.labels.item)\
            .format(sensortype.labels.format_str)\
            .icon(f'{sensortype}{area.lower()}')\
            .groups(sensor.item_ids.merged_sensor, f'{sensortype}{location}')\
            .location_item(location)\
            .sensor(sensortype.point, sensor.influxdb_tags)\
            .semantic(PointType.MEASUREMENT, sensortype.typed.property)\
            .channel(sensor.points.channel(sensortype.point))\
            .aisensor(AISensorDataType.NUMERICAL)\
            .append_to(self)

        if sensortype.typed.unit:
            sensor_item.unit(sensortype.typed.unit)

        sensor_item = self.moisture_items(sensortype, sensor_item, sensor)

        sensor_item = self.pressure_sealevel_items(
            sensortype, sensor_item, sensor)

        sensor_item = self.trend_items(sensortype, sensor_item, sensor)

        if sensortype.labels.has_gui_factor:
            String(f'gui{sensortype}{sensor.item_ids.sensor}')\
                .label(sensortype.labels.item)\
                .transform_js(f'gui{sensortype}')\
                .icon(f'{sensortype}{area.lower()}')\
                .groups(sensor.item_ids.merged_sensor, f'gui{sensortype}{location}')\
                .semantic(PointType.MEASUREMENT, sensortype.typed.property)\
                .channel(sensor.points.channel(sensortype.point),
                         ProfileType.JS, f'togui{sensortype.labels.gui_factor}.js')\
                .append_to(self)

    def moisture_items(self, sensortype: SensorType, sensor_item: BaseItem, sensor: Sensor) -> BaseItem:
        if sensortype == SensorType.MOISTURE:
            sensor_item\
                .scripting({
                    'reminder_item': sensor.item_ids.moisturelastreminder,
                    'watered_item': sensor.item_ids.moisturelastwatered
                })

            DateTime(sensor.item_ids.moisturelastreminder)\
                .label(_('Last watering reminder'))\
                .datetime()\
                .config()\
                .groups(sensor.item_ids.merged_sensor)\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .scripting({
                    'message': _('The plant {plant} needs to be watered!')
                    .format(plant=sensor.blankname)
                })\
                .append_to(self)

            DateTime(sensor.item_ids.moisturelastwatered)\
                .label(_('Last watered'))\
                .dateonly_weekday()\
                .icon('wateringcan')\
                .config()\
                .groups(sensor.item_ids.merged_sensor)\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .scripting({
                    'message': _('The plant {plant} says thank you for watering!')
                    .format(plant=sensor.blankname)
                })\
                .append_to(self)

        return sensor_item

    def pressure_sealevel_items(self,
                                sensortype: SensorType,
                                sensor_item: BaseItem,
                                sensor: Sensor) -> BaseItem:
        if sensortype == SensorType.PRESSURE and sensor.has_altitude:
            location = sensor.location
            area = location.area

            sensor_item\
                .scripting({
                    'pressure_sealevel_item': sensor.item_ids.pressure_sealevel,
                    'altitude': sensor.altitude
                })\
                .groups('PressureSealevel')\
                .remove_group(f'{sensortype}{location}')\
                .remove_sensor()

            Number(f'pressureSeaLevel{sensor.item_ids.merged_sensor}')\
                .typed(sensortype.typed.number)\
                .label(sensortype.labels.item)\
                .format(sensortype.labels.format_str)\
                .icon(f'{sensortype}{area.lower()}')\
                .groups(sensor.item_ids.merged_sensor, f'{sensortype}{location}')\
                .semantic(PointType.MEASUREMENT, sensortype.typed.property)\
                .sensor(sensortype.point, sensor.influxdb_tags)\
                .append_to(self)

        return sensor_item

    def trend_items(self, sensortype: SensorType, sensor_item: BaseItem, sensor: Sensor) -> BaseItem:
        if sensor.location.area == 'Outdoor' or sensortype == SensorType.PRESSURE:
            String(f'trend{sensortype}{sensor.item_ids.merged_sensor}')\
                .label(_('Trend {label}').format(label=sensortype.labels.item))\
                .map(MapTransformation.TREND)\
                .icon(f'trend{sensortype}')\
                .groups(sensor.item_ids.merged_sensor)\
                .semantic(PointType.STATUS)\
                .aisensor(AISensorDataType.CATEGORICAL)\
                .append_to(self)

            sensor_item\
                .groups('Trend')\
                .scripting({
                    'trend_item': f'trend{sensortype}{sensor.item_ids.merged_sensor}'
                })

            if sensortype == SensorType.TEMPERATURE:
                Number(f'average7d{sensortype}{sensor.item_ids.merged_sensor}')\
                    .label(_('7 days average {label}').format(label=sensortype.labels.item))\
                    .icon('average7d')\
                    .groups(sensor.item_ids.merged_sensor)\
                    .semantic(PointType.STATUS)\
                    .aisensor(AISensorDataType.NUMERICAL)\
                    .append_to(self)

                sensor_item\
                    .groups('Average7d')\
                    .scripting({
                        'average_item': f'average7d{sensortype}{sensor.item_ids.merged_sensor}'
                    })

        return sensor_item
