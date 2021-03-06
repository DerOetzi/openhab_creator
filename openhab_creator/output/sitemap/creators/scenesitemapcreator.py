from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation, Scene
from openhab_creator.models.sitemap import Page, Setpoint, Sitemap, Switch
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@SitemapCreatorPipeline(mainpage=0, configpage=0)
class SceneSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        frame = sitemap.second_frame
        page = Page(Scene.sceneactive_id)\
            .label(_('Scene'))\
            .map(MapTransformation.SCENE)\
            .append_to(frame)

        Switch(Scene.sceneactive_id, Scene.switch_mappings('normal'))\
            .label(_('Scenes'))\
            .append_to(page)

        Switch(Scene.sceneactive_id, Scene.switch_mappings('food'))\
            .label(_('Food scenes'))\
            .append_to(page)

        Switch(Scene.sceneactive_id, Scene.switch_mappings('special'))\
            .label(_('Special scenes'))\
            .append_to(page)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for scene items"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        page = Page(Scene.sceneactive_id)\
            .label(_('Time controlled'))\
            .map(MapTransformation.SCENE)\
            .append_to(configpage)

        self._build_timesframe(page)
        self._build_locationassignment(page, configuration)

    def _build_timesframe(self, page: Page) -> None:
        timesframe = page.frame('times', _('Time controlled'))

        workingday = Page(label=_('Working days'))\
            .icon('clock')\
            .append_to(timesframe)
        weekend = Page(label=_('Weekend and holidays'))\
            .icon('clock')\
            .append_to(timesframe)

        for scene in Scene:
            if scene.has_time:
                Setpoint(scene.timeworkingday_id,
                         scene.begin, scene.end)\
                    .append_to(workingday)

                Setpoint(scene.timeweekend_id,
                         scene.begin, scene.end)\
                    .append_to(weekend)

    @staticmethod
    def _build_locationassignment(page: Page,
                                  configuration: Configuration) -> None:
        for location in configuration.locations.timecontrolled.values():
            toplevel = location
            while toplevel.has_parent:
                toplevel = toplevel.parent

            frame = page.frame(toplevel.identifier, toplevel.name)
            subpage = Page(location.autoactive_id)\
                .label(location.name)\
                .icon('configuration')\
                .append_to(frame)

            for scene in Scene:
                Switch(location.sceneassignment_id(scene),
                       [('OFF', _('Off')), ('ON', _('On'))])\
                    .append_to(subpage)

            configframe = subpage.frame('config', _('Configuration'))

            Switch(location.autoweekend_id,
                   [('OFF', _('Off')), ('ON', _('On'))])\
                .append_to(configframe)

            Switch(location.autoguest_id,
                   [('OFF', _('Always')), ('ON', _('Only'))])\
                .append_to(configframe)
