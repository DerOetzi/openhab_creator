from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from openhab_creator.models.configuration.equipment.types.sensor import (
    Sensor, SensorType)
from openhab_creator.models.items import Group
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.location import Location


@ItemsCreatorPipeline(6)
class SensorItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        sensors = {
            'Indoor': {},
            'Outdoor': {}
        }

        for sensortype in SensorType:
            for sensor in configuration.equipment(sensortype.point):
                location = sensor.location
                area = location.area

                if sensortype not in sensors[area]:
                    sensors[area][sensortype] = {}

                if location not in sensors[area][sensortype]:
                    sensors[area][sensortype][location] = []

                sensors[area][sensortype][location].append(sensor)

        self.__build_indoor(sensors['Indoor'])

    def __build_indoor(self, sensors: Dict[SensorType, Dict[Location, List[Sensor]]]) -> None:
        for sensortype, locatedsensors in sensors.items():
            Group(f'{sensortype}Indoor')\
                .typed(sensortype.grouptype)\
                .label(sensortype.label)\
                .format(sensortype.format_string)\
                .append_to(self)

            self.__build_indoor_locatedsensors(sensortype, locatedsensors)

            self.write_file(sensortype.point)

    def __build_indoor_locatedsensors(self, sensortype: SensorType, locatedsensors: Dict[Location, List[Sensor]]) -> None:
        for location, sensors in locatedsensors.items():
            Group(f'{sensortype}{location}')\
                .label(location.name)\
                .format(sensortype.format_string)\
                .groups(f'{sensortype}Indoor')\
                .location(location)\
                .append_to(self)

            self.__build_indoor_sensors(sensortype, location, sensors)

    def __build_indoor_sensors(self, sensortype: SensorType, location: Location, sensors: List[Sensor]) -> None:
        for sensor in sensors:
            sensor_group = f'{sensortype}{sensor.semantic}{sensor.identifier}'
            sensor_equipment = Group(sensor_group)\
                .append_to(self)
