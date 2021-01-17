from __future__ import annotations

import re
from typing import Dict, List, Optional


class BaseElement(object):
    def __init__(self,
                 label: Optional[str] = None,
                 item: Optional[str] = None,
                 icon: Optional[str] = None):

        self._attributes = {}

        if item is not None:
            self._attributes['item'] = item

        if label is not None:
            self._attributes['label'] = f'"{label}"'

        if icon is not None:
            self._attributes['icon'] = f'"{icon}"'

        self._elements: List[BaseElement] = []

    def append(self, element: BaseElement) -> None:
        self._elements.append(element)

    def dump(self, typed: str, additional: Optional[Dict[str, str]] = {}) -> str:
        attributes = {**self._attributes, **additional}

        attributes_str = "\n    ".join(
            [key + '=' + value for key, value in attributes.items()])

        return f'{typed} {attributes_str}{self.dump_elements()}'

    def dump_elements(self) -> str:
        if len(self._elements) == 0:
            return ''

        lines = []
        for element in self._elements:
            lines.append(element.dump())

        block = "\n".join(lines)
        block = re.sub('^', ' '*4, block, flags=re.MULTILINE)

        return " {\n" + block + "\n}"
