from __future__ import annotations

import csv
import json
import os
from copy import deepcopy
from typing import Dict, Final, List

from openhab_creator import logger
from openhab_creator.exception import ConfigurationException
from openhab_creator.models.configuration.equipment.bridge import Bridge
from openhab_creator.models.configuration.location import (Location,
                                                           LocationFactory)


class SecretsStorage(object):
    def __init__(self, configdir: str, anonym: bool):
        self.__STORAGE: Final[Dict[str, str]] = {}
        self.__ANONYM: Final[bool] = anonym
        self.__MISSING_KEYS: Final[List[str]] = []

        if not anonym:
            self.__read_secrets(configdir)

    def __read_secrets(self, configdir: str) -> None:
        with open(os.path.join(configdir, 'secrets.csv')) as secretsfile:
            reader = csv.DictReader(secretsfile)

            for row in reader:
                key = row['key'].lower()
                if row['value'].strip() == '':
                    logger.warning(f"Empty secret: {key}")
                    self.__STORAGE[key] = '__%s__' % (
                        key.upper())
                else:
                    self.__STORAGE[key.lower()] = row['value'].strip()

    @property
    def anonym(self) -> bool:
        return self.__ANONYM

    @property
    def secrets(self) -> Dict[str, str]:
        return deepcopy(self.__STORAGE)

    def secret(self, *args: List[str]) -> str:
        key = '_'.join(args).lower()

        if key in self.__STORAGE:
            value = self.__STORAGE[key]
        else:
            if key not in self.__MISSING_KEYS:
                self.__MISSING_KEYS.append(key)
            value = "__%s__" % key.upper()

        return value

    @property
    def has_missing(self) -> bool:
        return len(self.__MISSING_KEYS) > 0 and not self.anonym

    def handle_missing(self) -> bool:
        if self.has_missing:
            logger.error("Missing secrets:")
            for key in self.__MISSING_KEYS:
                logger.error(key)

        return self.has_missing


class Configuration(object):
    def __init__(self, name: str, configdir: str, anonym: bool):
        self.__SECRETS_STORAGE = SecretsStorage(configdir, anonym)
        self.__init_bridges(configdir)
        self.__init_templates(configdir)
        self.__init_locations(configdir)

    def __init_bridges(self, configdir: str) -> None:
        self.__BRIDGES: Final[Dict[str, Bridge]] = {}

        bridges = self.__read_jsons_from_dir(configdir, 'bridges')

        for bridge_key, bridge_configuration in bridges.items():
            self.__BRIDGES[bridge_key] = Bridge(
                configuration=self, **bridge_configuration)

    def __init_templates(self, configdir: str) -> None:
        self.__TEMPLATES: Final[Dict[str, Dict]] = self.__read_jsons_from_dir(
            configdir, 'templates')

    def __init_locations(self, configdir: str) -> None:
        self.__LOCATIONS: Final[Dict[str, List[Location]]] = {}

        self.__init_floors(configdir)

    def __init_floors(self, configdir: str) -> None:
        self.__LOCATIONS['floors'] = []

        floors = self.__read_jsons_from_dir(
            configdir, 'locations/indoor/floors')

        for floor_key in sorted(floors.keys()):
            self.__LOCATIONS['floors'].append(LocationFactory.new(
                configuration=self, **floors[floor_key]))

    def __read_jsons_from_dir(self, configdir: str, subdir: str) -> Dict[str, Dict]:
        results = {}

        srcdir = os.path.join(configdir, subdir)

        if os.path.exists(srcdir):
            for dir_entry in os.scandir(srcdir):
                name = os.path.basename(dir_entry)
                if name.endswith('.json'):
                    with open(dir_entry) as json_file:
                        results[name[:-5].lower()] = json.load(json_file)

        return results

    @property
    def bridges(self) -> Dict[str, Bridge]:
        return self.__BRIDGES

    def bridge(self, bridge_key: str) -> Bridge:
        bridge_key = bridge_key.lower()
        if bridge_key not in self.bridges:
            raise ConfigurationException(
                f'No bridge "{bridge_key}" in configuration')

        return self.bridges[bridge_key]

    @property
    def templates(self) -> Dict[str, Dict]:
        return self.__TEMPLATES

    def template(self, template_key: str) -> Dict:
        template_key = template_key.lower()
        if template_key not in self.templates:
            raise ConfigurationException(
                f'No template "{template_key}" in configuration')

        return deepcopy(self.templates[template_key])

    @property
    def secrets(self) -> SecretsStorage:
        return self.__SECRETS_STORAGE
