from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator.models.location.room import Room
from openhab_creator.models.sitemap.frame import Frame
from openhab_creator.models.sitemap.text import Text
from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.thing.equipment.lightbulb import Lightbulb


class LightbulbSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, lightbulbs: List[Lightbulb]) -> Text:
        frames = {}

        page = Text('Lights')

        for lightbulb in lightbulbs:
            location = lightbulb.location()

            if isinstance(location, Room):
                location = location.floor()

            if location.identifier() in frames:
                frame = frames[location.identifier()]
            else:
                frame = Frame(location.name())
                frames[location.identifier()] = frame
                page.append(frame)

            frame.append(Text(lightbulb.name()))

        return page
