from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Type

from openhab_creator import _
from openhab_creator.models.sitemap.frame import Frame

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator


class SitemapCreatorRegistry(object):
    CREATORS_REGISTRY = []

    def __init__(self, mainpage: Optional[int] = -1,
                 statuspage: Optional[int] = -1,
                 configpage: Optional[int] = -1):
        self._mainpage_order: int = mainpage
        self._statuspage_order: int = statuspage
        self._configpage_order: int = configpage

    def __call__(self, cls: Type[BaseSitemapCreator]) -> Type[BaseSitemapCreator]:
        SitemapCreatorRegistry.CREATORS_REGISTRY.append({
            "mainpage": self._mainpage_order,
            "statuspage": self._statuspage_order,
            "configpage": self._configpage_order,
            "class": cls
        })
        return cls

    @staticmethod
    def pipeline_mainpage(configuration: SmarthomeConfiguration) -> Frame:
        creators = SitemapCreatorRegistry.__creators('mainpage')

        frame = Frame()

        for creator in creators:
            print(
                f'Sitemap creator (mainpage) {creator["mainpage"]} {creator["class"].__name__}')
            c = creator['class']()
            frame.append(c.build_mainpage(configuration))

        return frame

    @staticmethod
    def pipeline_configpage(configuration: SmarthomeConfiguration) -> Frame:
        creators = SitemapCreatorRegistry.__creators('configpage')

        frame = Frame(_('Configuration'))

        for creator in creators:
            print(
                f'Sitemap creator (configpage) {creator["configpage"]} {creator["class"].__name__}')
            c = creator['class']()
            frame.append(c.build_configpage(configuration))

        return frame

    @staticmethod
    def __creators(typed: str) -> List[BaseSitemapCreator]:
        filtered = filter(
            lambda creator: creator[typed] > -1, SitemapCreatorRegistry.CREATORS_REGISTRY)

        return sorted(filtered, key=lambda creator: creator[typed])
