from __future__ import annotations

import re
from typing import List, Optional


class BaseElement(object):
    def __init__(self, label: Optional[str] = None, item: Optional[str] = None):
        self._label: str = label
        self._item: str = item

        self._elements: List[BaseElement] = []

    def append(self, element: BaseElement) -> None:
        self._elements.append(element)

    def labelstring(self) -> str:
        if self._label is None:
            return ''

        return f'label="{self._label}"'

    def itemstring(self) -> str:
        if self._item is None:
            return ''

        return f'item={self._label}'

    def dump_elements(self) -> str:
        if len(self._elements) == 0:
            return ''

        lines = []
        for element in self._elements:
            lines.append(element.dump())

        block = "\n".join(lines)
        block = re.sub('^', ' '*4, block, flags=re.MULTILINE)

        return "{\n" + block + "\n}"
