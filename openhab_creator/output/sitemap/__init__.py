from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, List, Optional, Type, Dict, Union

from openhab_creator import _, logger
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

        second_frame = sitemap.second_frame

        SitemapCreatorPipeline.build_mainpage(sitemap, configuration)

        statuspage = Page(label=_('State')).icon('status')
        SitemapCreatorPipeline.build_statuspage(statuspage, configuration)

        configpage = Page(label=_('Configuration')).icon('configuration')
        SitemapCreatorPipeline.build_configpage(configpage, configuration)

        second_frame\
            .element(statuspage)\
            .element(configpage)

        self.append(sitemap.dump())
        self.write_file('default')


class SitemapCreatorPipeline():
    mainpage_pipeline: List[Dict[str, Union[int, BaseSitemapCreator]]] = []
    statuspage_pipeline: List[Dict[str, Union[int, BaseSitemapCreator]]] = []
    configpage_pipeline: List[Dict[str, Union[int, BaseSitemapCreator]]] = []
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
                .append({'order': self.mainpage, 'class': sitemapcreator_cls})

        if self.statuspage > -1:
            SitemapCreatorPipeline.statuspage_pipeline\
                .append({'order': self.statuspage, 'class': sitemapcreator_cls})

        if self.configpage > -1:
            SitemapCreatorPipeline.configpage_pipeline\
                .append({'order': self.configpage, 'class': sitemapcreator_cls})

        return sitemapcreator_cls

    @classmethod
    def _init(cls):
        if not cls.initialized:
            import_module(
                'openhab_creator.output.sitemap.creators')

            cls.initialized = True

    @classmethod
    def build_mainpage(cls, sitemap: Sitemap, configuration: Configuration) -> None:
        cls._init()
        for creator in sorted(cls.mainpage_pipeline, key=lambda x: x['order']):
            creator_cls = creator['class']
            if creator_cls.has_needed_equipment(configuration):
                logger.info('Sitemap creator (mainpage): %s',
                            creator_cls.__name__)
                creator = creator_cls()
                creator.build_mainpage(sitemap, configuration)

    @classmethod
    def build_statuspage(cls, statuspage: Page, configuration: Configuration) -> None:
        cls._init()
        for creator in sorted(cls.statuspage_pipeline, key=lambda x: x['order']):
            creator_cls = creator['class']
            if creator_cls.has_needed_equipment(configuration):
                logger.info('Sitemap creator (statuspage): %s',
                            creator_cls.__name__)
                creator = creator_cls()
                creator.build_statuspage(statuspage, configuration)

    @classmethod
    def build_configpage(cls, configpage: Page, configuration: Configuration) -> None:
        cls._init()
        for creator in sorted(cls.configpage_pipeline, key=lambda x: x['order']):
            creator_cls = creator['class']
            if creator_cls.has_needed_equipment(configuration):
                logger.info('Sitemap creator (configpage): %s',
                            creator_cls.__name__)
                creator = creator_cls()
                creator.build_configpage(configpage, configuration)
