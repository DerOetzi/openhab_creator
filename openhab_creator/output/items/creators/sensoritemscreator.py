from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorType)
from openhab_creator.models.items import (DateTime, Group, GroupType, Number,
                                          PointType, ProfileType, PropertyType,
                                          String)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.location import Location


@ItemsCreatorPipeline(6)
class SensorItemsCreator(BaseItemsCreator):
    def __init__(self, outputdir: str):
        super().__init__(outputdir)
        self.sensors = {}

    def build(self, configuration: Configuration) -> None:
        Group('Trend')\
            .append_to(self)

        for sensor in configuration.equipment.equipment('sensor'):
            location = sensor.location
            area = location.area

            if area not in self.sensors:
                self.sensors[area] = {}

            self.build_sensor(sensor)

            if sensor.has_subequipment:
                for subsensor in sensor.subequipment:
                    if sensor.category != 'sensor':
                        self.build_sensor(subsensor)

                    self.build_sensortype_area(subsensor)
            else:
                self.build_sensortype_area(sensor)

        self.write_file('sensors')

    def build_sensor(self, sensor: Sensor) -> None:
        sensor_equipment = Group(sensor.item_ids.sensor)\
            .semantic('Sensor')

        if sensor.sensor_is_subequipment:
            sensor_equipment\
                .label(_('Sensor'))\
                .equipment(sensor)
        else:
            sensor_equipment\
                .label(_('Sensor {blankname}').format(blankname=sensor.blankname))\
                .location(sensor.location)

        sensor_equipment.append_to(self)

    def build_sensortype_area(self, sensor: Sensor) -> None:
        area = sensor.location.area

        for sensortype in SensorType:
            if sensortype.point in sensor.categories:
                if sensortype not in self.sensors[area]:
                    self.sensors[area][sensortype] = {}
                    Group(f'{sensortype}{area}')\
                        .typed(GroupType.NUMBER_AVG)\
                        .label(sensortype.labels.item)\
                        .format(sensortype.labels.format_str)\
                        .icon(f'{sensortype}{area.lower()}')\
                        .append_to(self)

                    if sensortype.labels.has_gui_factor:
                        Group(f'gui{sensortype}{area}')\
                            .typed(GroupType.NUMBER_AVG)\
                            .label(sensortype.labels.item)\
                            .transform_js(f'gui{sensortype}')\
                            .icon(f'{sensortype}{area.lower()}')\
                            .append_to(self)

                self.build_sensortype_location(sensortype, sensor)

    def build_sensortype_location(self, sensortype: SensorType, sensor: Sensor) -> None:
        location = sensor.location
        area = location.area

        if location not in self.sensors[area][sensortype]:
            self.sensors[area][sensortype][location] = True
            Group(f'{sensortype}{location}')\
                .typed(GroupType.NUMBER_AVG)\
                .label(sensortype.labels.item)\
                .format(sensortype.labels.format_str)\
                .icon(f'{sensortype}{area.lower()}')\
                .groups(f'{sensortype}{area}')\
                .location(location)\
                .semantic(PointType.MEASUREMENT, sensortype.typed.property)\
                .append_to(self)

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

        sensor_item = Number(f'{sensortype}{sensor.item_ids.sensor}')\
            .typed(sensortype.typed.number)\
            .label(sensortype.labels.item)\
            .format(sensortype.labels.format_str)\
            .icon(f'{sensortype}{area.lower()}')\
            .groups(sensor.item_ids.merged_sensor, f'{sensortype}{location}', 'Trend')\
            .semantic(PointType.MEASUREMENT, sensortype.typed.property)\
            .channel(sensor.points.channel(sensortype.point))\
            .sensor(sensortype.point, sensor.influxdb_tags)\
            .aisensor()

        if sensortype.point == 'moisture':
            sensor_item.scripting({
                'reminder_item': sensor.item_ids.moisturelastreminder,
                'watered_item': sensor.item_ids.moisturelastwatered
            })

            self.moisture_items(sensor)

        sensor_item.append_to(self)

        String(f'trend{sensortype}{sensor.item_ids.sensor}')\
            .label(_('Trend {label}').format(label=sensortype.labels.item))\
            .map(MapTransformation.TREND)\
            .groups(sensor.item_ids.merged_sensor)\
            .semantic(PointType.STATUS)\
            .aisensor()\
            .append_to(self)

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

    def moisture_items(self, sensor: Sensor) -> None:
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
