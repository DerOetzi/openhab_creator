from __future__ import annotations

from openhab_creator import __version__, logger
from openhab_creator.models.configuration import Configuration
from openhab_creator.models.items.baseitem import BaseItem
from openhab_creator.output.content import (AutomationCreator,
                                            BasicConfigCreator, IconsCreator,
                                            MapTransformationCreator)
from openhab_creator.output.documentationcreator import DocumentationCreator
from openhab_creator.output.items import ItemsCreator
from openhab_creator.output.sitemap import SitemapCreator
from openhab_creator.output.things import ThingsCreator


class Creator():
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
        logger.info("openHAB Configuration Creator (%s)", __version__)
        logger.info("Output directory: %s", self.outputdir)

        configuration = Configuration(self.name, self.configdir, self.anonym)

        if configuration.secrets.handle_missing() or self.check_only:
            return

        BasicConfigCreator(self.outputdir).build(configuration)

        ThingsCreator(self.outputdir).build(configuration)
        ItemsCreator(self.outputdir).build(configuration)

        SitemapCreator(self.outputdir).build(configuration)

        MapTransformationCreator(self.outputdir).build()
        AutomationCreator(self.outputdir).build(self.configdir, configuration)

        if self.icons:
            icons_creator = IconsCreator(self.outputdir)
            icons_creator.build(self.configdir)
            icons_creator.check_icons_exist(BaseItem.icons)

        DocumentationCreator(self.configdir).build(configuration)
