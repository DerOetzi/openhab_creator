from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING

import json

from copy import deepcopy
from io import BufferedReader, TextIOWrapper

from openhab_creator import __version__

from openhab_creator.exception import ConfigurationException
from openhab_creator.secretsregistry import SecretsRegistry

from openhab_creator.models import ConfigurationType
from openhab_creator.models.location import Location
from openhab_creator.models.location.floor import Floor
from openhab_creator.models.location.manager import LocationManager
from openhab_creator.models.location.room import Room
from openhab_creator.models.thing.bridge import Bridge
from openhab_creator.models.thing.manager import BridgeManager
from openhab_creator.models.equipment import Equipment
from openhab_creator.models.equipment.manager import EquipmentManager

from openhab_creator.output.thingscreator import ThingsCreator
from openhab_creator.output.itemscreator import ItemsCreator


class Creator(object):
    def __init__(self, configfile: BufferedReader, outputdir: str, secretsfile: TextIOWrapper, check_only: bool):
        self._config_json: ConfigurationType = json.load(configfile)
        self._outputdir: str = outputdir
        self._secretsfile: TextIOWrapper = secretsfile
        self._check_only: bool = check_only

        self._templates: Dict = self._config_json['templates']

        self._bridges: BridgeManager = BridgeManager()
        self._locations: LocationManager = LocationManager()
        self._equipment: EquipmentManager = EquipmentManager()

    def run(self) -> None:
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self._outputdir)

        if self._secretsfile is not None:
            SecretsRegistry.init(self._secretsfile)

        self.parse()

        things_creator = ThingsCreator(self._outputdir, self._check_only)
        things_creator.build(self._bridges)

        items_creator = ItemsCreator(self._outputdir, self._check_only)
        items_creator.build(self._locations, self._equipment)

        if self._secretsfile is not None:
            SecretsRegistry.handle_missing()

    def parse(self) -> None:
        self._parse_bridges()

        for location in self._config_json['locations'].values():
            self._parse_floors(location)

    def _parse_bridges(self) -> None:
        for bridge_key, bridge in self._config_json['bridges'].items():
            self._bridges.register(bridge_key, Bridge(bridge))

    def _parse_floors(self, location_configuration: ConfigurationType) -> None:
        if 'floors' in location_configuration:
            for floor_configuration in location_configuration['floors']:
                floor = Floor(floor_configuration)
                self._locations.register_floor(floor)
                self._parse_equipment(floor_configuration, floor)
                self._parse_rooms(floor_configuration, floor)

    def _parse_rooms(self, floor_configuration: ConfigurationType, floor: Floor) -> None:
        if 'rooms' in floor_configuration:
            for room_configuration in floor_configuration['rooms']:
                room = Room(room_configuration, floor)
                self._parse_equipment(room_configuration, room)

    def _parse_equipment(self, parent_configuration: ConfigurationType, location: Location) -> None:
        if 'equipment' in parent_configuration:
            for equipment_configuration in parent_configuration['equipment']:
                equipment_configuration = self._merge_template(
                    equipment_configuration)
                equipment = Equipment(
                    equipment_configuration, location, self._bridges)
                self._equipment.register(equipment)

    def _merge_template(self, equipment_configuration: ConfigurationType) -> ConfigurationType:
        if 'template' in equipment_configuration:
            template = self.__template_deepcopy(
                equipment_configuration['template'])
            equipment_configuration.pop('template', None)
            for key, value in template.items():
                if key not in equipment_configuration:
                    equipment_configuration[key] = value

        if 'equipment' in equipment_configuration:
            subequipment_configuration_merged = []
            for subequipment_configuration in equipment_configuration['equipment']:
                subequipment_configuration_merged.append(
                    self._merge_template(subequipment_configuration))

            equipment_configuration['equipment'] = subequipment_configuration_merged

        return equipment_configuration

    def __template_deepcopy(self, template_name: str) -> ConfigurationType:
        if template_name not in self._templates:
            raise ConfigurationException(
                'Template %s not found' % template_name)

        return deepcopy(self._templates[template_name])
