from __future__ import annotations

import json
import os
from typing import Dict, Final
from copy import deepcopy

from openhab_creator.exception import ConfigurationException
from openhab_creator.models.configuration.equipment.bridge import Bridge


class Configuration(object):
    def __init__(self, name: str, configdir: str):
        self.__init_bridges(configdir)
        self.__init_templates(configdir)

    def __init_bridges(self, configdir: str) -> None:
        self.__BRIDGES: Final[Dict[str, Bridge]] = {}

        bridges = self.__read_jsons_from_dir(configdir, 'bridges')

        for bridge_key, bridge_configuration in bridges.items():
            self.__BRIDGES[bridge_key] = Bridge(**bridge_configuration)

    def __init_templates(self, configdir: str) -> None:
        self.__TEMPLATES: Final[Dict[str, Dict]] = self.__read_jsons_from_dir(
            configdir, 'templates')

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
