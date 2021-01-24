from __future__ import annotations

import re
from typing import TYPE_CHECKING

import openhab_creator.output.sitemap.creators
from openhab_creator.models.sitemap.frame import Frame
from openhab_creator.models.sitemap.text import Text
from openhab_creator.output.basecreator import BaseCreator
from openhab_creator.output.sitemap.sitemapcreatorpipeline import \
    SitemapCreatorPipeline

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration


class SitemapCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('sitemap', outputdir, 'sitemaps')

    def build(self, configuration: SmarthomeConfiguration):

        self._append(f'sitemap default label="{configuration.name()}" {{')

        mainpage_frame = SitemapCreatorPipeline.pipeline_mainpage(
            configuration).dump()

        mainpage_frame = re.sub('^', ' '*4, mainpage_frame, flags=re.MULTILINE)
        self._append(mainpage_frame)

        second_frame = Frame()

        statuspage = Text(label='Status', icon='smarthome')
        statuspage.append(
            SitemapCreatorPipeline.pipeline_configpage(configuration))
        second_frame.append(statuspage)

        self._append(
            re.sub('^', ' '*4, second_frame.dump(), flags=re.MULTILINE))

        self._append('}')

        self._write_file('default')
