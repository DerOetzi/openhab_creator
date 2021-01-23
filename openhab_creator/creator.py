from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict

from openhab_creator import __version__
from openhab_creator.models.configuration import SmarthomeConfiguration
from openhab_creator.models.secretsregistry import SecretsRegistry
from openhab_creator.output.content.basicconfigcreator import \
    BasicConfigCreator
from openhab_creator.output.content.iconscreator import IconsCreator
from openhab_creator.output.content.automationcreator import AutomationCreator
from openhab_creator.output.items.itemscreator import ItemsCreator
from openhab_creator.output.sitemap.sitemapcreator import SitemapCreator
from openhab_creator.output.things.thingscreator import ThingsCreator


class Creator(object):
    def __init__(self, name: str,
                 configdir: str, outputdir: str,
                 anonym: bool, check_only: bool,
                 icons: bool, all: bool,
                 automation: bool):

        self._name: str = name
        self._configdir: str = configdir
        self._outputdir: str = outputdir
        self._anonym: bool = anonym
        self._check_only: bool = check_only
        self._icons: bool = icons
        self._all: bool = all
        self._automation: bool = automation

    def run(self) -> None:
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self._outputdir)

        if self._all:
            basic_creator = BasicConfigCreator(self._outputdir)
            basic_creator.build()

        if not self._anonym:
            SecretsRegistry.init(self._configdir)

        configuration = SmarthomeConfiguration(self._name, self._configdir)

        if not self._anonym and SecretsRegistry.has_missing():
            SecretsRegistry.handle_missing()
            return

        if self._check_only:
            return

        things_creator = ThingsCreator(self._outputdir)
        things_creator.build(configuration)

        items_creator = ItemsCreator(self._outputdir)
        items_creator.build(configuration)

        sitemap_creator = SitemapCreator(self._outputdir)
        sitemap_creator.build(configuration)

        if self._automation or self._all:
            AutomationCreator(self._outputdir).build(self._configdir)

        if self._icons or self._all:
            IconsCreator(self._outputdir).build()
