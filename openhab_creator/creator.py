from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict

from openhab_creator import __version__
from openhab_creator.models.configuration import SmarthomeConfiguration
from openhab_creator.output.itemscreator import ItemsCreator
from openhab_creator.output.thingscreator import ThingsCreator
from openhab_creator.output.sitemapcreator import SitemapCreator
from openhab_creator.models.secretsregistry import SecretsRegistry

if TYPE_CHECKING:
    from io import BufferedReader, TextIOWrapper


class Creator(object):
    def __init__(self, configfile: BufferedReader, outputdir: str, secretsfile: TextIOWrapper, check_only: bool):
        self.__json_config: Dict = json.load(configfile)
        self._outputdir: str = outputdir
        self._secretsfile: TextIOWrapper = secretsfile
        self._check_only: bool = check_only

    def run(self) -> None:
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self._outputdir)

        if self._secretsfile is not None:
            SecretsRegistry.init(self._secretsfile)

        configuration = SmarthomeConfiguration(**self.__json_config)

        things_creator = ThingsCreator(self._outputdir, self._check_only)
        things_creator.build(configuration)

        items_creator = ItemsCreator(self._outputdir, self._check_only)
        items_creator.build(configuration)

        sitemap_creator = SitemapCreator(self._outputdir, self._check_only)
        sitemap_creator.build(configuration)

        if self._secretsfile is not None:
            SecretsRegistry.handle_missing()
