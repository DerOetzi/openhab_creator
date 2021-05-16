from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from openhab_creator import _
from openhab_creator.models.sitemap.baseelement import BaseElement
from openhab_creator.models.sitemap.text import Text

if TYPE_CHECKING:
    from openhab_creator.models.configuration.baseobject import BaseObject


class Frame(BaseElement):
    def __init__(self, label: Optional[str] = ''):
        super().__init__(label=label)

    @property
    def elementtype(self) -> str:
        return 'Frame'

    def dump(self) -> str:
        output = ''
        if self.has_elements:
            output = super().dump()

        return output


class Page(Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_frame: Frame = Frame()
        super().element(self.main_frame)
        self.frames: Dict[Frame] = {}

    def element(self, element: BaseElement) -> Page:
        return self.main_frame.element(element)

    def frame(self, identifier: str, label: Optional[str] = '') -> Frame:
        if identifier not in self.frames:
            self.frames[identifier] = Frame(label)
            super().element(self.frames[identifier])

        return self.frames[identifier]

    @property
    def has_elements(self) -> bool:
        return self.main_frame.has_elements or len(self.frames) > 0

    def dump(self) -> str:
        output = ''
        if self.has_elements:
            output = super().dump()

        return output


class Sitemap(Page):
    def __init__(self, name: str, label: str):
        self.name = name
        super().__init__(label=label)

    @property
    def second_frame(self) -> Frame:
        return self.frame('second', _('State and configuration'))

    @property
    def elementtype(self) -> str:
        return f'sitemap {self.name}'
