from __future__ import annotations

import re
from typing import TYPE_CHECKING

import openhab_creator.output.sitemap.creators
from openhab_creator.models.sitemap.frame import Frame
from openhab_creator.output.basecreator import BaseCreator
from openhab_creator.output.sitemap.sitemapcreatorregistry import \
    SitemapCreatorRegistry

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration


class SitemapCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('sitemap', outputdir, 'sitemaps')

    def build(self, configuration: SmarthomeConfiguration):

        self._append(f'sitemap default label="{configuration.name()}" {{')

        mainpage_frame = SitemapCreatorRegistry.pipeline_mainpage(
            configuration).dump()

        mainpage_frame = re.sub('^', ' '*4, mainpage_frame, flags=re.MULTILINE)
        self._append(mainpage_frame)

        self._append('}')

        self._write_file('default')
