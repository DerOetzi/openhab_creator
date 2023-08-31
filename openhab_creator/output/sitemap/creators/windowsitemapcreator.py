from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.sitemap import Page, Sitemap, Text, Setpoint, Switch
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.grafana import Dashboard


@SitemapCreatorPipeline(statuspage=60, configpage=20)
class WindowSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('window', False)

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        """No mainpage for window items"""

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        windows = configuration.equipment.equipment('window')

        page = Page('windows')\
            .append_to(statuspage)

        for window in windows:
            toplevel_location = window.location.toplevel
            frame = page.frame(
                toplevel_location.identifier, toplevel_location.name)

            Text(window.item_ids.windowopen)\
                .label(window.name)\
                .map(MapTransformation.WINDOWOPEN)\
                .append_to(frame)

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        windows = configuration.equipment.equipment('window')
        page = Page(label=_('Windows'))\
            .icon('window')\
            .append_to(configpage)

        for window in windows:
            if window.remindertime:
                location = window.location
                frame = page.frame(
                    location.identifier, location.name)

                Setpoint(window.item_ids.remindertime, 0, 15)\
                    .label(_('{name} reminder time').format(name=window.name))\
                    .append_to(frame)

                Switch(window.item_ids.sendreminder, [('OFF', _('Inactive')), ('ON', _('Active'))])\
                    .append_to(frame)
