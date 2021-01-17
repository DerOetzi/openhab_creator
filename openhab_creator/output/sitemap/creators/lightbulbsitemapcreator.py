from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _
from openhab_creator.models.location.room import Room
from openhab_creator.models.sitemap.frame import Frame
from openhab_creator.models.sitemap.switch import Switch
from openhab_creator.models.sitemap.text import Text
from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator
from openhab_creator.output.sitemap.sitemapcreatorregistry import SitemapCreatorRegistry

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.thing.equipment.types.lightbulb import Lightbulb


@SitemapCreatorRegistry(0)
class LightbulbSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, configuration: SmarthomeConfiguration) -> Text:
        frames = {}

        page = Text(_('Lights'))

        for lightbulb in configuration.equipment('lightbulb'):
            location = lightbulb.location()

            if isinstance(location, Room):
                location = location.floor()

            if location.identifier() in frames:
                frame = frames[location.identifier()]
            else:
                frame = Frame(location.name())
                frames[location.identifier()] = frame
                page.append(frame)

            frame.append(self._create_control(lightbulb))

        return page

    def _create_control(self, lightbulb: Lightbulb) -> Switch:
        return Switch(lightbulb.name(), lightbulb.lightcontrol_id())
