from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorType)
from openhab_creator.models.items import Group, Number, PointType, String
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
        for sensor in configuration.equipment('sensor'):
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
        sensor_equipment = Group(sensor.sensor_id)\
            .semantic('Sensor')

        if sensor.sensor_is_subequipment:
            sensor_equipment\
                .label(_('Sensor'))\
                .groups(sensor.equipment_id)
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
                        .typed(sensortype.grouptype)\
                        .label(sensortype.labelitem)\
                        .format(sensortype.format_string)\
                        .icon(f'{sensortype}{area.lower()}')\
                        .append_to(self)

                self.build_sensortype_location(sensortype, sensor)

    def build_sensortype_location(self, sensortype: SensorType, sensor: Sensor) -> None:
        location = sensor.location
        area = location.area

        if location not in self.sensors[area][sensortype]:
            self.sensors[area][sensortype][location] = True
            Group(f'{sensortype}{location}')\
                .typed(sensortype.grouptype)\
                .label(sensortype.labelitem)\
                .format(sensortype.format_string)\
                .icon(f'{sensortype}{area.lower()}')\
                .groups(f'{sensortype}{area}')\
                .location(location)\
                .semantic(PointType.MEASUREMENT, sensortype.propertytype)\
                .append_to(self)

        Number(f'{sensortype}{sensor.sensor_id}')\
            .typed(sensortype.numbertype)\
            .label(sensortype.labelitem)\
            .format(sensortype.format_string)\
            .icon(f'{sensortype}{area.lower()}')\
            .groups(sensor.merged_sensor_id, f'{sensortype}{location}')\
            .semantic(PointType.MEASUREMENT, sensortype.propertytype)\
            .channel(sensor.channel(sensortype.point))\
            .sensor(sensortype.point, sensor.influxdb_tags)\
            .append_to(self)

        String(f'trend{sensortype}{sensor.sensor_id}')\
            .label(_('Trend {label}').format(label=sensortype.labelitem))\
            .map(MapTransformation.TREND)\
            .groups(sensor.merged_sensor_id)\
            .semantic(PointType.STATUS)\
            .sensor(f'trend{sensortype.point}', sensor.influxdb_tags)\
            .append_to(self)
