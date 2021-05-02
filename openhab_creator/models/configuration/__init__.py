from __future__ import annotations

import csv
import json
import os
from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator import logger
from openhab_creator.exception import ConfigurationException
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.bridge import Bridge
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


class Configuration():
    WITHOUT_CHILDS = 'without_childs'
    WITH_CHILDS = 'with_childs'

    def __init__(self, name: str, configdir: str, anonym: bool):
        self.configdir: str = configdir
        self.name: str = name
        self.secrets: SecretsStorage = SecretsStorage(configdir, anonym)
        self.equipment_registry: Dict[str, Dict[str, List[Equipment]]] = {
            'battery': {
                self.WITHOUT_CHILDS: [],
                self.WITH_CHILDS: []
            }
        }
        self.dashboard: Dashboard = Dashboard(self)
        self.timecontrolled_locations: Dict[str, Location] = {}
        self.macs: Dict[str, Equipment] = {}

        self._init_bridges(configdir)
        self._init_templates(configdir)

        self._init_persons(configdir)

        self._init_locations(configdir)

        if len(self.macs) > 0:
            for lan in self.equipment('lan', False):
                lan.register_macs(self.macs)

    def _init_bridges(self, configdir: str) -> None:
        self.bridges: Dict[str, Bridge] = {}

        bridges = self._read_jsons_from_dir(configdir, 'bridges')

        for bridge_key, bridge_configuration in bridges.items():
            self.bridges[bridge_key] = Bridge(
                configuration=self, **bridge_configuration)

    def _init_persons(self, configdir: str) -> None:
        self.persons: List[Person] = []
        with open(f'{configdir}/persons.json', encoding='utf-8') as json_file:
            persons = json.load(json_file)
            key = 0
            for person_equipment in persons:
                self.persons.append(Person(self, key, person_equipment))
                key += 1

    def _init_templates(self, configdir: str) -> None:
        EquipmentType.init(self._read_jsons_from_dir(
            configdir, 'templates'))

    def _init_locations(self, configdir: str) -> None:
        self.locations: Dict[str, List[Location]] = {}

        self._init_floors(configdir)
        self._init_buildings(configdir)
        self._init_outdoors(configdir)

    def _init_floors(self, configdir: str) -> None:
        self.locations['floors'] = []

        floors = self._read_jsons_from_dir(
            configdir, 'locations/indoor/floors')

        for floor_key in sorted(floors.keys()):
            self.locations['floors'].append(LocationFactory.new(
                configuration=self, **floors[floor_key]))

    def _init_buildings(self, configdir: str) -> None:
        self.locations['buildings'] = []

        buildings = self._read_json_from_file(
            configdir, 'locations/indoor/buildings.json')

        for building in buildings:
            self.locations['buildings'].append(
                LocationFactory.new(configuration=self, **building))

    def _init_outdoors(self, configdir: str) -> None:
        self.locations['outdoors'] = []

        outdoors = self._read_json_from_file(
            configdir, 'locations/outdoors.json')

        for outdoor in outdoors:
            self.locations['outdoors'].append(
                LocationFactory.new(configuration=self, **outdoor))

    @staticmethod
    def _read_json_from_file(configdir: str, filename: str) -> List[Dict]:
        results = []

        srcfile = os.path.join(configdir, filename)

        if os.path.exists(srcfile):
            with open(srcfile, encoding='utf-8') as json_file:
                results = json.load(json_file)

        return results

    @staticmethod
    def _read_jsons_from_dir(configdir: str, subdir: str) -> Dict[str, Dict]:
        results = {}

        srcdir = os.path.join(configdir, subdir)

        if os.path.exists(srcdir):
            for dir_entry in os.scandir(srcdir):
                name = os.path.basename(dir_entry)
                if name.endswith('.json'):
                    with open(dir_entry, encoding='utf-8') as json_file:
                        results[name[:-5].lower()] = json.load(json_file)

        return results

    def bridge(self, bridge_key: str) -> Bridge:
        bridge_key = bridge_key.lower()
        if bridge_key not in self.bridges:
            raise ConfigurationException(
                f'No bridge "{bridge_key}" in configuration')

        return self.bridges[bridge_key]

    @property
    def floors(self) -> List[Location]:
        return self.locations['floors']

    @property
    def buildings(self) -> List[Location]:
        return self.locations['buildings']

    @property
    def outdoors(self) -> List[Location]:
        return self.locations['outdoors']

    def add_equipment(self, equipment: Equipment):
        for category in equipment.categories:
            if category not in self.equipment_registry:
                self.equipment_registry[category] = {
                    self.WITHOUT_CHILDS: [],
                    self.WITH_CHILDS: []
                }

            self.equipment_registry[category][self.WITH_CHILDS].append(
                equipment)

            if not equipment.is_child:
                self.equipment_registry[category][self.WITHOUT_CHILDS].append(
                    equipment)

        if equipment.is_timecontrolled:
            location = equipment.location
            self.timecontrolled_locations[location.identifier] = location

    def has_equipment(self, category: str,
                      filter_childs: Optional[bool] = True) -> bool:
        return len(self.equipment(category, filter_childs)) > 0

    def equipment(self, category: str,
                  filter_childs: Optional[bool] = True) -> List[Equipment]:
        if category in self.equipment_registry:
            equipment_registry = self.equipment_registry[category]
        else:
            equipment_registry = {
                self.WITHOUT_CHILDS: [],
                self.WITH_CHILDS: []
            }

        if filter_childs:
            equipment = equipment_registry[self.WITHOUT_CHILDS]
        else:
            equipment = equipment_registry[self.WITH_CHILDS]

        return equipment

    def register_mac(self, equipment: Equipment) -> str:
        mac = self.secrets.secret(
            'tr064', 'lan', 'mac', equipment.semantic, equipment.identifier)

        self.macs[mac] = equipment
        return mac
