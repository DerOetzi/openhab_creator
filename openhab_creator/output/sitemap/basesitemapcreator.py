from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openhab_creator.models.sitemap.baseelement import BaseElement
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.sitemap import Sitemap, Page


class BaseSitemapCreator(object):
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_mainpage")

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_statuspage")

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build_configpage")

    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return True
