from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict, Final

from openhab_creator import __version__, logger
from openhab_creator.models.configuration import Configuration
from openhab_creator.output.content.automationcreator import AutomationCreator
from openhab_creator.output.content.basicconfigcreator import \
    BasicConfigCreator
from openhab_creator.output.content.iconscreator import IconsCreator
from openhab_creator.output.things.thingscreator import ThingsCreator


class Creator(object):
    def __init__(self, name: str,
                 configdir: str, outputdir: str,
                 anonym: bool, check_only: bool,
                 icons: bool):

        self.name: str = name
        self.configdir: str = configdir
        self.outputdir: str = outputdir
        self.anonym: bool = anonym
        self.check_only: bool = check_only
        self.icons: bool = icons

    def run(self) -> None:
        logger.info(f"openHAB Configuration Creator ({__version__})")
        logger.info(f"Output directory: {self.outputdir}")

        configuration = Configuration(self.name, self.configdir, self.anonym)

        if configuration.secrets.handle_missing() or self.check_only:
            return

        BasicConfigCreator(self.outputdir).build()

        ThingsCreator(self.outputdir).build(configuration)

        AutomationCreator(self.outputdir).build(self.configdir, configuration)

        if self.icons:
            IconsCreator(self.outputdir).build()
