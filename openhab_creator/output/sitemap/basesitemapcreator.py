from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openhab_creator.models.sitemap.baseelement import BaseElement
    from openhab_creator.models.configuration import SmarthomeConfiguration


class BaseSitemapCreator(object):
    def build_mainpage(self, configuration: SmarthomeConfiguration) -> BaseElement:
        raise NotImplementedError("Must override build")

    def build_configpage(self, configuration: SmarthomeConfiguration) -> BaseElement:
        raise NotImplementedError("Must override build")
