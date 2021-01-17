from __future__ import annotations

from typing import TYPE_CHECKING, Type

from openhab_creator.models.sitemap.frame import Frame

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator


class SitemapCreatorRegistry(object):
    CREATORS_REGISTRY = []

    def __init__(self, mainpage_order: int):
        self._mainpage_order: int = mainpage_order

    def __call__(self, cls: Type[BaseSitemapCreator]) -> Type[BaseSitemapCreator]:
        SitemapCreatorRegistry.CREATORS_REGISTRY.append({
            "mainpage": self._mainpage_order,
            "class": cls
        })
        return cls

    @staticmethod
    def pipeline_mainpage(configuration: SmarthomeConfiguration) -> Frame:
        creators = sorted(SitemapCreatorRegistry.CREATORS_REGISTRY,
                          key=lambda creator: creator['mainpage'])

        frame = Frame()

        for creator in creators:
            print(
                f'Sitemap creator (mainpage) {creator["mainpage"]} {creator["class"].__name__}')
            c = creator['class']()
            frame.append(c.build_mainpage(configuration))

        return frame
