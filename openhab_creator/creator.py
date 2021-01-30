from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict

from openhab_creator import __version__

from openhab_creator.models.configuration import Configuration
from openhab_creator.models.configuration.equipment import EquipmentFactory


class Creator(object):
    def __init__(self, name: str,
                 configdir: str, outputdir: str,
                 anonym: bool, check_only: bool,
                 icons: bool, all: bool,
                 automation: bool):

        self.__name: str = name
        self.__configdir: str = configdir
        self.__outputdir: str = outputdir
        self.__anonym: bool = anonym
        self.__check_only: bool = check_only
        self.__icons: bool = icons
        self.__all: bool = all
        self.__automation: bool = automation

    @property
    def name(self) -> str:
        return self.__name

    @property
    def configdir(self) -> str:
        return self.__configdir

    def run(self) -> None:
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self.__outputdir)

        configuration = Configuration(self.name, self.configdir)

        test_equipment = {
            'name': 'Test',
            'template': 'dimmablelight'
        }

        equipment = EquipmentFactory.new(configuration, **test_equipment)
