from __future__ import annotations

import re
from abc import abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from openhab_creator.output.formatter import Formatter

if TYPE_CHECKING:
    from openhab_creator import CreatorEnum
    from openhab_creator.models.common import MapTransformation
    from openhab_creator.output.color import Color


class BaseElement():
    def __init__(self, item: Optional[str] = None, label: Optional[str] = ''):
        self.attributes: Dict[str, str] = {}

        self._format_str: Optional[str] = None
        self.label(label)

        self.attribute('item', item)
        self.elements: List[BaseElement] = []

    @property
    @abstractmethod
    def elementtype(self) -> str:
        pass

    def item(self, item: Optional[str] = None) -> BaseElement:
        return self.attribute('item', item)

    def label(self, label: Optional[str] = '') -> BaseElement:
        self._label = label
        return self.attribute('label', Formatter.label(self._label, self._format_str), '"', '"')

    @property
    def labelstr(self) -> str:
        return self._label

    def map(self, mapname: MapTransformation) -> BaseElement:
        return self.format(mapname.formatstr)

    def format(self, format_str: Optional[str] = None) -> BaseElement:
        self._format_str = format_str
        return self.attribute('label', Formatter.label(self._label, self._format_str), '"', '"')

    def icon(self, icon: str) -> BaseElement:
        return self.attribute('icon', icon, '"', '"')

    def visibility(self, *visibility: List[Tuple[str, str, Union[str, CreatorEnum]]]) -> BaseElement:
        return self.attribute('visibility',
                              Formatter.key_value_tuples(
                                  visibility, separator=",\n           "),
                              '[', ']')

    def labelcolor(self, *labelcolors: List[Tuple[str, Union[str, Color]]]) -> BaseElement:
        return self.attribute('labelcolor',
                              Formatter.key_value_tuples(
                                  labelcolors, separator=",\n              "),
                              '[', ']')

    def valuecolor(self, *valuecolors: List[Tuple[str, Union[str, Color]]]) -> BaseElement:
        return self.attribute('valuecolor',
                              Formatter.key_value_tuples(
                                  valuecolors, separator=",\n              "),
                              '[', ']')

    def element(self, element: BaseElement) -> BaseElement:
        self.elements.append(element)
        return self

    def append_to(self, parent_element: BaseElement) -> BaseElement:
        parent_element.element(self)
        return self

    def dump(self) -> str:
        element_attributes = Formatter.key_value_pairs(
            self.attributes, separator="\n  ", escape=False)

        length = len(self.elementtype) - 1

        element_attributes = re.sub(
            '^', ' '*length, element_attributes, flags=re.MULTILINE)

        return f'{self.elementtype} {element_attributes[length:]}{self.dump_elements()}'

    def dump_elements(self) -> str:
        output = ''
        if self.has_elements:
            lines = []
            for element in self.elements:
                lines.append(element.dump())

            block = "\n".join(lines)
            block = re.sub('^', ' '*4, block, flags=re.MULTILINE)

            output = " {\n" + block + "\n}"

        return output

    @property
    def has_elements(self) -> bool:
        return len(self.elements) > 0

    def attribute(self,
                  key: str,
                  attr: Optional[str] = None,
                  prefix: Optional[str] = '',
                  suffix: Optional[str] = '') -> BaseElement:
        if attr is None:
            self.attributes.pop(key, None)
        else:
            self.attributes[key] = f'{prefix}{attr}{suffix}'

        return self
