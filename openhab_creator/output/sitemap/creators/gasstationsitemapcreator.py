from __future__ import annotations

from typing import List, Tuple

from openhab_creator import _
from openhab_creator.models.configuration import Configuration
from openhab_creator.models.configuration.equipment.types.gasstation import (
    FuelType, GasStation)
from openhab_creator.models.sitemap import Frame, Page, Sitemap, Text
from openhab_creator.output.color import Color
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator


@SitemapCreatorPipeline(mainpage=80)
class GasStationSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('gasstation')

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        page = Page(label=_('Fuel prices'))\
            .icon('gasstation')\
            .append_to(sitemap)

        for fueltype in FuelType:
            frame = page.frame(fueltype.identifier, fueltype.label)

            for gasstation in configuration.equipment.equipment('gasstation'):
                self._build_gasstation(frame, fueltype, gasstation)

        self._add_grafana(configuration.dashboard, page,
                          [_('Price development')])

    def _build_gasstation(self, frame: Frame, fueltype: FuelType, gasstation: GasStation) -> None:
        Text(gasstation.item_ids.price(fueltype))\
            .label(gasstation.blankname)\
            .visibility((gasstation.item_ids.opened, '==', 'OPEN'))\
            .valuecolor(*self.valuecolor(gasstation.item_ids.difference(fueltype)))\
            .append_to(frame)

    @staticmethod
    def valuecolor(item: str) -> List[Tuple[str, Color]]:
        return [
            (f'{item}>=5', Color.RED),
            (f'{item}>=3', Color.ORANGE),
            (f'{item}>=1', Color.YELLOW),
            (f'{item}==0', Color.GREEN)
        ]

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for indoor sensors"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for indoor sensors"""
