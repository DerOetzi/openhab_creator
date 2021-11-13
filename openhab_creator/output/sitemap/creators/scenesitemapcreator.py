from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation, Scene
from openhab_creator.models.sitemap import (Page, Selection, Setpoint, Sitemap,
                                            Switch)
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

        Switch('autoScene', [('ON', _('Automation'))])\
            .visibility(('autoScene', '!=', 'ON'))\
            .append_to(page)

        config_frame = page.frame('config_frame', _('Configuration'))

        Switch('wayhome', [
            ('OFF', _('Away')),
            ('ON', _('Way home'))
        ])\
            .visibility(
                ('Presences', '==', 0),
                (Scene.sceneactive_id, '==', 'Absence'),
                ('wayhome', '==', 'ON')
        )\
            .append_to(config_frame)

        Switch('overridePresence', [
            ('OFF', _('Inactive')),
            ('ON', _('Active'))
        ])\
            .append_to(config_frame)

        Switch('autoGuestStayed', [
            ('OFF', _('No guest')),
            ('ON', _('Guest'))
        ])\
            .append_to(config_frame)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for scene items"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        page = Page(Scene.sceneactive_id)\
            .label(_('Time controlled'))\
            .map(MapTransformation.SCENE)\
            .append_to(configpage)

        self._build_timesframe(page)
        self._build_locationassignment(page, configuration)

    @staticmethod
    def _build_timesframe(page: Page) -> None:
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
                Selection(location.sceneassignment_id(scene),
                          [('OFF', _('Off')),
                           ('ALWAYS', _('Always')),
                           ('WORKINGDAY', _('Working days')),
                           ('WEEKEND', _('Weekend')),
                           ('GUEST', _('Guest stayed'))])\
                    .append_to(subpage)
