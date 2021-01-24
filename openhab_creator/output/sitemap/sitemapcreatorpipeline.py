from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Type

from openhab_creator import _
from openhab_creator.models.sitemap.frame import Frame

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator


class SitemapCreatorPipeline(object):
    CREATORS_REGISTRY = []

    def __init__(self, mainpage: Optional[int] = -1,
                 statuspage: Optional[int] = -1,
                 configpage: Optional[int] = -1,
                 equipment_needed: Optional[List[str]] = []):
        self._mainpage_order: int = mainpage
        self._statuspage_order: int = statuspage
        self._configpage_order: int = configpage
        self._equipment_needed: List[str] = equipment_needed

    def __call__(self, cls: Type[BaseSitemapCreator]) -> Type[BaseSitemapCreator]:
        SitemapCreatorPipeline.CREATORS_REGISTRY.append({
            "mainpage": self._mainpage_order,
            "statuspage": self._statuspage_order,
            "configpage": self._configpage_order,
            "needed": self._equipment_needed,
            "class": cls
        })
        return cls

    @staticmethod
    def pipeline_mainpage(configuration: SmarthomeConfiguration) -> Frame:
        creators = SitemapCreatorPipeline.__creators('mainpage', configuration)

        frame = Frame()

        for creator in creators:
            print(
                f'Sitemap creator (mainpage) {creator["mainpage"]} {creator["class"].__name__}')
            c = creator['class']()
            frame.append(c.build_mainpage(configuration))

        return frame

    @staticmethod
    def pipeline_configpage(configuration: SmarthomeConfiguration) -> Frame:
        creators = SitemapCreatorPipeline.__creators(
            'configpage', configuration)

        frame = Frame(_('Configuration'))

        for creator in creators:
            print(
                f'Sitemap creator (configpage) {creator["configpage"]} {creator["class"].__name__}')
            c = creator['class']()
            frame.append(c.build_configpage(configuration))

        return frame

    @staticmethod
    def __creators(typed: str, configuration: SmarthomeConfiguration) -> List[BaseSitemapCreator]:
        filtered = filter(
            lambda creator: SitemapCreatorPipeline.__filter(creator, typed, configuration), SitemapCreatorPipeline.CREATORS_REGISTRY)

        return sorted(filtered, key=lambda creator: creator[typed])

    @staticmethod
    def __filter(creator, typed: str, configuration: SmarthomeConfiguration) -> bool:
        if creator[typed] == -1:
            return False

        for needed in creator['needed']:
            if configuration.has_equipment(needed):
                return True

        return False
