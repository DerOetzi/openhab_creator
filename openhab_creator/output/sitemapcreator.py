from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator.models.sitemap.frame import Frame
from openhab_creator.output.basecreator import BaseCreator
from openhab_creator.output.sitemap.lightbulbsitemapcreator import LightbulbSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration


class SitemapCreator(BaseCreator):
    def __init__(self, outputdir: str, check_only: bool):
        super().__init__('sitemap', outputdir, check_only, 'sitemaps')

    def build(self, configuration: SmarthomeConfiguration):

        main_frame = Frame()

        lightbulb_creator = LightbulbSitemapCreator()
        main_frame.append(lightbulb_creator.build_mainpage(
            configuration.lightbulbs()))

        self._append(f'sitemap default label="{configuration.name()}" {{')
        self._append(main_frame.dump())

        self._append('}')

        self._write_file('default')
