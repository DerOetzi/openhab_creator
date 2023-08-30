from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _
from openhab_creator.models.configuration import Configuration
from openhab_creator.models.configuration.equipment.types.poweroutlet import \
    PowerOutlet
from openhab_creator.models.sitemap import (OnOffSwitch, Page, Selection,
                                            Sitemap)
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.wallswitch import \
        WallSwitch


@SitemapCreatorPipeline(mainpage=75, configpage=15)
class PowerOutletSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('poweroutlet')

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        page = Page(label=_('Poweroutlets'))\
            .icon('poweroutlet')\

        poweroutlets = 0

        for poweroutlet in configuration.equipment.equipment('poweroutlet'):
            if not poweroutlet.poweroutlet_is_subequipment:
                if self._build_poweroutlet_switch(page, poweroutlet):
                    poweroutlets += 1

        if poweroutlets > 0:
            page.append_to(sitemap)

    def _build_poweroutlet_switch(self, page: Page, poweroutlet: PowerOutlet) -> bool:
        created = False

        if poweroutlet.points.has_onoff:
            location = poweroutlet.location.toplevel
            frame = page.frame(location.identifier, location.name)

            OnOffSwitch(poweroutlet.item_ids.onoff)\
                .label(poweroutlet.blankname)\
                .append_to(frame)

            created = True

        return created

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for indoor sensors"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        page = Page(label=_('Poweroutlets'))\
            .icon('poweroutlet')\

        poweroutlets = 0

        has_wallswitches, wallswitches = configuration.equipment.has(
            'wallswitch')

        if has_wallswitches:
            for poweroutlet in configuration.equipment.equipment('poweroutlet'):
                if not poweroutlet.poweroutlet_is_subequipment:
                    if self._build_poweroutlet_config(page, poweroutlet, wallswitches):
                        poweroutlets += 1

        if poweroutlets > 0:
            page.append_to(configpage)

    def _build_poweroutlet_config(self, page: Page,
                                  poweroutlet: PowerOutlet,
                                  wallswitches: List[WallSwitch]) -> bool:
        created = False

        if poweroutlet.points.has_onoff:
            location = poweroutlet.location.toplevel
            frame = page.frame(location.identifier, location.name)

            poweroutlet_page = Page(label=poweroutlet.blankname)\
                .icon('poweroutlet')\
                .append_to(frame)

            for wallswitch in wallswitches:
                self._build_poweroutlet_config_buttons_assignment(
                    poweroutlet_page, poweroutlet, wallswitch)

            created = True

        return created

    def _build_poweroutlet_config_buttons_assignment(
            self,
            page: Page,
            poweroutlet: PowerOutlet,
            wallswitch: WallSwitch) -> None:

        location = wallswitch.location.toplevel
        frame = page.frame(location.identifier, location.name)

        subpage = Page(
            label=_('Assignment {wallswitch} to {lightbulb}').format(
                wallswitch=wallswitch.name, lightbulb=poweroutlet.name))\
            .icon('configuration')\
            .append_to(frame)

        for button_key in range(0, wallswitch.buttons_count):
            Selection(wallswitch.item_ids.buttonassignment(
                button_key, poweroutlet), [
                ('NULL', _('No assignment')),
                ('ON', _('On')),
                ('OFF', _('Off'))
            ])\
                .append_to(subpage)
