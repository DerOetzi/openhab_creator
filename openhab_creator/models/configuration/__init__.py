from __future__ import annotations

import csv
import json
import os
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from openhab_creator import logger
from openhab_creator.exception import ConfigurationException
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.bridge import Bridge
from openhab_creator.models.configuration.equipment.types.learninghouse import LearningHouse
from openhab_creator.models.configuration.location import (Location,
                                                           LocationFactory)
from openhab_creator.models.configuration.person import Person
from openhab_creator.models.grafana.dashboard import Dashboard

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment import Equipment
    from openhab_creator.models.configuration.equipment.types.networkappliance import \
        NetworkAppliance


class SecretsStorage():
    def __init__(self, configdir: str, anonym: bool):
        self.storage: Dict[str, str] = {}
        self.anonym: bool = anonym
        self.missing_keys: List[str] = []

        if not anonym:
            self.__read_secrets(configdir)

    def __read_secrets(self, configdir: str) -> None:
        with open(os.path.join(configdir, 'secrets.csv')) as secretsfile:
            reader = csv.DictReader(secretsfile)

            for row in reader:
                key = row['key'].lower()
                if row['value'].strip() == '':
                    logger.warning("Empty secret: %s", key)
                    self.storage[key] = '__%s__' % (
                        key.upper())
                else:
                    self.storage[key.lower()] = row['value'].strip()

    def secret(self, *args: List[str]) -> str:
        value = self.secret_optional(*args)

        if value is None:
            key = self.secret_key(*args)
            if key not in self.missing_keys:
                self.missing_keys.append(key)
            value = "__%s__" % key.upper()

        return value

    def secret_optional(self, *args: List[str]) -> Optional[str]:
        key = self.secret_key(*args)

        if key in self.storage:
            value = self.storage[key]
        else:
            value = None

        return value

    @staticmethod
    def secret_key(*args: List[str]) -> str:
        return '_'.join(args).lower()

    @property
    def has_missing(self) -> bool:
        return len(self.missing_keys) > 0 and not self.anonym

    def handle_missing(self) -> bool:
        if self.has_missing:
            logger.error("Missing secrets:")
            for key in self.missing_keys:
                logger.error(key)

        return self.has_missing


class EquipmentRegistry():
    WITHOUT_CHILDS = 'without_childs'
    WITH_CHILDS = 'with_childs'

    def __init__(self, configuration: Configuration):
        self.configuration: Configuration = configuration

        self.registry: Dict[str, Dict[str, List[Equipment]]] = {
            'battery': {
                self.WITHOUT_CHILDS: [],
                self.WITH_CHILDS: []
            }
        }

        self._init_bridges(configuration.configdir)
        self.macs: Dict[str, Equipment] = {}

    def _init_bridges(self, configdir: str) -> None:
        self.bridges: Dict[str, Bridge] = {}

        bridges = Configuration.read_jsons_from_dir(configdir, 'bridges')

        for bridge_key, bridge_configuration in bridges.items():
            bridge_configuration.pop('typed', None)

            self.bridges[bridge_key] = Bridge(
                configuration=self.configuration, **bridge_configuration)

    def has_bridge(self, bridge_key: str) -> bool:
        return bridge_key in self.bridges

    def bridge(self, bridge_key: str) -> Bridge:
        bridge_key = bridge_key.lower()
        if not self.has_bridge(bridge_key):
            raise ConfigurationException(
                f'No bridge "{bridge_key}" in configuration')

        return self.bridges[bridge_key]

    def add(self, equipment: Equipment):
        for category in equipment.categories:
            if category not in self.registry:
                self.registry[category] = {
                    self.WITHOUT_CHILDS: [],
                    self.WITH_CHILDS: []
                }

            self.registry[category][self.WITH_CHILDS].append(
                equipment)

            if not equipment.is_child:
                self.registry[category][self.WITHOUT_CHILDS].append(
                    equipment)

    def has(self, category: str,
            filter_childs: Optional[bool] = True,
            filter_categories: Optional[List[str]] = None) -> Tuple[bool, List[Equipment]]:
        equipment = self.equipment(category, filter_childs, filter_categories)

        return len(equipment) > 0, equipment

    def equipment(self, category: str,
                  filter_childs: Optional[bool] = True,
                  filter_categories: Optional[List[str]] = None) -> List[Equipment]:
        if category in self.registry:
            equipment_registry = self.registry[category]
        else:
            equipment_registry = {
                self.WITHOUT_CHILDS: [],
                self.WITH_CHILDS: []
            }

        if filter_childs:
            equipment = equipment_registry[self.WITHOUT_CHILDS]
        else:
            equipment = equipment_registry[self.WITH_CHILDS]

        if filter_categories is not None:
            for filter_category in filter_categories:
                equipment = list(
                    filter(lambda x, filter_category=filter_category: filter_category
                           in x.categories, equipment))

        return equipment

    def register_mac(self, equipment: Equipment) -> str:
        mac = self.configuration.secrets.secret(
            'tr064', 'lan', 'mac', equipment.semantic, equipment.identifier)

        self.macs[mac] = equipment
        return mac

    def init_lan(self) -> None:
        if len(self.macs) > 0:
            for lan in self.equipment('lan', False):
                lan.register_macs(self.macs)


class LocationRegistry():
    def __init__(self, configuration: Configuration):
        self.configuration: Configuration = configuration
        self.registry: Dict[str, List[Location]] = {}
        self.timecontrolled: Dict[str, Location] = {}

    def read_configuration(self) -> None:
        self._init_floors(self.configuration.configdir)
        self._init_buildings(self.configuration.configdir)
        self._init_outdoors(self.configuration.configdir)

    def _init_floors(self, configdir: str) -> None:
        floors = Configuration.read_jsons_from_dir(
            configdir, 'locations/indoor/floors')

        self._init_locations('floors', [floors[key]
                                        for key in sorted(floors.keys())])

        for floor in self.floors:
            for room in floor.rooms:
                if room.is_timecontrolled:
                    self.timecontrolled[room.identifier] = room

    def _init_buildings(self, configdir: str) -> None:
        buildings = Configuration.read_json_from_file(
            configdir, 'locations/indoor/buildings.json')

        self._init_locations('buildings', buildings)

    def _init_outdoors(self, configdir: str) -> None:
        outdoors = Configuration.read_json_from_file(
            configdir, 'locations/outdoors.json')

        self._init_locations('outdoors', outdoors)

    def _init_locations(self, location_key: str, locations: List[Dict]) -> None:
        self.registry[location_key] = []

        for location_definition in locations:
            location = LocationFactory.new(configuration=self.configuration,
                                           **location_definition)

            if location.is_timecontrolled:
                self.timecontrolled[location.identifier] = location

            self.registry[location_key].append(location)

    @property
    def floors(self) -> List[Location]:
        return self.registry['floors']

    @property
    def buildings(self) -> List[Location]:
        return self.registry['buildings']

    @property
    def outdoors(self) -> List[Location]:
        return self.registry['outdoors']


class GeneralRegistry():
    def __init__(self, configuration: Configuration):
        self.configuration: Configuration = configuration
        self.equipment: List[Equipment] = []
        self.learninghouse: List[str] = []

    def read_configuration(self) -> None:
        self.read_general()
        self.read_bridges()

    def read_general(self) -> None:
        general_configuration = self.configuration.read_json_from_file(
            self.configuration.configdir, 'general.json')

        for equipment_definition in general_configuration:
            equipment = EquipmentType.new(configuration=self.configuration,
                                          **equipment_definition)

            self.equipment.append(equipment)

            if isinstance(equipment, LearningHouse):
                self.learninghouse.append(equipment.item_ids.dependent)

    def read_bridges(self):
        bridges = Configuration.read_jsons_from_dir(
            self.configuration.configdir, 'bridges')

        for bridge_key, bridge_configuration in bridges.items():
            if 'typed' in bridge_configuration:
                bridge_configuration.pop('binding')
                bridge_configuration['thing']['bridge'] = bridge_key

                equipment = EquipmentType.new(configuration=self.configuration,
                                              **bridge_configuration)

                self.equipment.append(equipment)

    def has_learninghouse(self, dependent: str):
        return dependent in self.learninghouse


class Configuration():
    #pylint: disable=too-many-instance-attributes
    def __init__(self, name: str, configdir: str, anonym: bool):
        self.configdir: str = configdir
        self.name: str = name
        self.secrets: SecretsStorage = SecretsStorage(configdir, anonym)

        os.makedirs(os.path.join(
            configdir, 'documentation'), exist_ok=True)

        self.dashboard: Dashboard = Dashboard(self)

        self._init_templates(configdir)

        self.general: GeneralRegistry = GeneralRegistry(self)
        self.equipment: EquipmentRegistry = EquipmentRegistry(self)
        self.locations: LocationRegistry = LocationRegistry(self)

        self.general.read_configuration()
        self.locations.read_configuration()

        self._init_persons(configdir)

        self.equipment.init_lan()

    def _init_persons(self, configdir: str) -> None:
        self.persons: List[Person] = []
        with open(f'{configdir}/persons.json', encoding='utf-8') as json_file:
            persons = json.load(json_file)
            key = 0
            for person_equipment in persons:
                self.persons.append(Person(self, key, person_equipment))
                key += 1

    def _init_templates(self, configdir: str) -> None:
        EquipmentType.init(self.read_jsons_from_dir(
            configdir, 'templates'))

    @staticmethod
    def read_json_from_file(configdir: str, filename: str) -> List[Dict]:
        results = []

        srcfile = os.path.join(configdir, filename)

        if os.path.exists(srcfile):
            with open(srcfile, encoding='utf-8') as json_file:
                results = json.load(json_file)

        return results

    @staticmethod
    def read_jsons_from_dir(configdir: str, subdir: str) -> Dict[str, Dict]:
        results = {}

        srcdir = os.path.join(configdir, subdir)

        if os.path.exists(srcdir):
            for dir_entry in os.scandir(srcdir):
                name = os.path.basename(dir_entry)
                if name.endswith('.json'):
                    with open(dir_entry, encoding='utf-8') as json_file:
                        results[name[:-5].lower()] = json.load(json_file)

        return results
