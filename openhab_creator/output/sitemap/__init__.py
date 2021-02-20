from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, List, Optional, Type

from openhab_creator import _
from openhab_creator.models.sitemap import Page, Sitemap, Text
from openhab_creator.output.basecreator import BaseCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator


class SitemapCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('sitemap', outputdir, 'sitemaps')

    def build(self, configuration: Configuration) -> None:
        sitemap = Sitemap('default', configuration.name)

        SitemapCreatorPipeline.build_mainpage(sitemap, configuration)

        statuspage = Page(label=_('State'))

        configpage = Page(label=_('Configuration')).icon('configuration')
        SitemapCreatorPipeline.build_configpage(configpage, configuration)

        sitemap.frame('second', _('State and configuration'))\
            .element(statuspage)\
            .element(configpage)

        self.append(sitemap.dump())
        self.write_file('default')


class SitemapCreatorPipeline(object):
    mainpage_pipeline: List[BaseSitemapCreator] = []
    statuspage_pipeline: List[BaseSitemapCreator] = []
    configpage_pipeline: List[BaseSitemapCreator] = []
    initialized: bool = False

    def __init__(self,
                 mainpage: Optional[int] = -1,
                 statuspage: Optional[int] = -1,
                 configpage: Optional[int] = -1):
        self.mainpage: int = mainpage
        self.statuspage: int = statuspage
        self.configpage: int = configpage

    def __call__(self, sitemapcreator_cls: Type[BaseSitemapCreator]):
        if self.mainpage > -1:
            SitemapCreatorPipeline.mainpage_pipeline\
                .insert(self.mainpage, sitemapcreator_cls)

        if self.statuspage > -1:
            SitemapCreatorPipeline.statuspage_pipeline\
                .insert(self.statuspage, sitemapcreator_cls)

        if self.configpage > -1:
            SitemapCreatorPipeline.configpage_pipeline\
                .insert(self.configpage, sitemapcreator_cls)

    @classmethod
    def _init(cls):
        if not cls.initialized:
            import_module(
                'openhab_creator.output.sitemap.creators')

            cls.initialized = True

    @classmethod
    def build_mainpage(cls, sitemap: Sitemap, configuration: Configuration) -> None:
        cls._init()
        for creator in cls.mainpage_pipeline:
            if creator.has_needed_equipment(configuration):
                c = creator()
                c.build_mainpage(sitemap, configuration)

    @classmethod
    def build_configpage(cls, configpage: Page, configuration: Configuration) -> None:
        cls._init()
        for creator in cls.configpage_pipeline:
            if creator.has_needed_equipment(configuration):
                c = creator()
                c.build_configpage(configpage, configuration)
