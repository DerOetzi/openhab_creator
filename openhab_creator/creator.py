from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict

from openhab_creator import __version__, logger

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

    @property
    def anonym(self) -> bool:
        return self.__anonym

    def run(self) -> None:
        logger.info(f"openHAB Configuration Creator ({__version__})")
        logger.info(f"Output directory: {self.__outputdir}")

        configuration = Configuration(self.name, self.configdir, self.anonym)

        if configuration.secrets.handle_missing():
            return
