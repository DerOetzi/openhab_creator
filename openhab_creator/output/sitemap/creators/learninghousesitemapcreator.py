from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.sitemap import Page, Sitemap, Switch, Text
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@SitemapCreatorPipeline(statuspage=30)
class LearningHouseSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('learninghouse')

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        """No mainpage for learninghouse"""

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        page = Page(label=_('LearningHouse'))\
            .icon('learninghouse')\
            .append_to(statuspage)

        for learninghouse in configuration.equipment.equipment('learninghouse'):
            Text(learninghouse.item_ids.dependent)\
                .append_to(page)

            Switch(learninghouse.item_ids.train, [
                   ('OFF', _('Wrong')), ('ON', _('Correct'))])\
                .append_to(page)

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for learninghouse"""
