from __future__ import annotations

import csv
import json
import os
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, List

from openhab_creator import logger
from openhab_creator.exception import ConfigurationException
from openhab_creator.models.configuration.equipment.bridge import Bridge
from openhab_creator.models.configuration.location import (Location,
                                                           LocationFactory)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment import Equipment


class SecretsStorage(object):
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
                    logger.warning(f"Empty secret: {key}")
                    self.storage[key] = '__%s__' % (
                        key.upper())
                else:
                    self.storage[key.lower()] = row['value'].strip()

    def secret(self, *args: List[str]) -> str:
        key = '_'.join(args).lower()

        if key in self.storage:
            value = self.storage[key]
        else:
            if key not in self.missing_keys:
                self.missing_keys.append(key)
            value = "__%s__" % key.upper()

        return value

    @property
    def has_missing(self) -> bool:
        return len(self.missing_keys) > 0 and not self.anonym

    def handle_missing(self) -> bool:
        if self.has_missing:
            logger.error("Missing secrets:")
            for key in self.missing_keys:
                logger.error(key)

        return self.has_missing


class Configuration(object):
    def __init__(self, name: str, configdir: str, anonym: bool):
        self.secrets = SecretsStorage(configdir, anonym)
        self.equipment_registry: Dict[str, List[Equipment]] = {}
        self._init_bridges(configdir)
        self._init_templates(configdir)
        self._init_locations(configdir)

    def _init_bridges(self, configdir: str) -> None:
        self.bridges: Dict[str, Bridge] = {}

        bridges = self.read_jsons_from_dir(configdir, 'bridges')

        for bridge_key, bridge_configuration in bridges.items():
            self.bridges[bridge_key] = Bridge(
                configuration=self, **bridge_configuration)

    def _init_templates(self, configdir: str) -> None:
        self.templates: Dict[str, Dict] = self.read_jsons_from_dir(
            configdir, 'templates')

    def _init_locations(self, configdir: str) -> None:
        self.locations: Dict[str, List[Location]] = {}

        self._init_floors(configdir)

    def _init_floors(self, configdir: str) -> None:
        self.locations['floors'] = []

        floors = self.read_jsons_from_dir(
            configdir, 'locations/indoor/floors')

        for floor_key in sorted(floors.keys()):
            self.locations['floors'].append(LocationFactory.new(
                configuration=self, **floors[floor_key]))

    def read_jsons_from_dir(self, configdir: str, subdir: str) -> Dict[str, Dict]:
        results = {}

        srcdir = os.path.join(configdir, subdir)

        if os.path.exists(srcdir):
            for dir_entry in os.scandir(srcdir):
                name = os.path.basename(dir_entry)
                if name.endswith('.json'):
                    with open(dir_entry) as json_file:
                        results[name[:-5].lower()] = json.load(json_file)

        return results

    def bridge(self, bridge_key: str) -> Bridge:
        bridge_key = bridge_key.lower()
        if bridge_key not in self.bridges:
            raise ConfigurationException(
                f'No bridge "{bridge_key}" in configuration')

        return self.bridges[bridge_key]

    def template(self, template_key: str) -> Dict:
        template_key = template_key.lower()
        if template_key not in self.templates:
            raise ConfigurationException(
                f'No template "{template_key}" in configuration')

        return deepcopy(self.templates[template_key])

    @property
    def floors(self) -> List[Location]:
        return self.locations['floors']

    def add_equipment(self, equipment: Equipment):
        category = equipment.category

        if category not in self.equipment_registry:
            self.equipment_registry[category] = []

        self.equipment_registry[category].append(equipment)

    def has_equipment(self, category: str) -> bool:
        return category in self.equipment_registry and len(self.equipment_registry[category]) > 0

    def equipment(self, category: str) -> List[Equipment]:
        if not self.has_equipment(category):
            raise ConfigurationException(
                f'No Equipment with category {category}')

        return self.equipment_registry[category]
