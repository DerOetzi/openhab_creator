from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Tuple

from openhab_creator.models.sitemap.frame import Frame

if TYPE_CHECKING:
    from openhab_creator.models.baseobject import BaseObject
    from openhab_creator.models.sitemap.baseelement import BaseElement
    from openhab_creator.models.configuration import SmarthomeConfiguration


class BaseSitemapCreator(object):
    def __init__(self):
        self.__page_frames: Dict[str, Frame] = {}

    def _page_frame(self, obj: BaseObject) -> Tuple[Frame, bool]:
        is_new = False
        if obj.identifier() in self.__page_frames:
            frame = self.__page_frames[obj.identifier()]
        else:
            frame = Frame(obj.name())
            self.__page_frames[obj.identifier()] = frame
            is_new = True

        return frame, is_new

    def _clear_page_frames(self) -> None:
        self.__page_frames.clear()

    def build_mainpage(self, configuration: SmarthomeConfiguration) -> BaseElement:
        raise NotImplementedError("Must override build")

    def build_configpage(self, configuration: SmarthomeConfiguration) -> BaseElement:
        raise NotImplementedError("Must override build")
