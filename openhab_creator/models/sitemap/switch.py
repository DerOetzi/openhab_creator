from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from openhab_creator.models.sitemap.baseelement import BaseElement


class Switch(BaseElement):
    def __init__(self, **args):
        self._mappings: Dict[str, Tuple[int, str]] = args.pop('mappings')
        self._mappings = sorted(self._mappings, key=lambda tup: tup[0])

        super().__init__(**args)

    def dump(self) -> str:
        mappings = '[' + ",".join([f'{command}="{label}"' for order, command,
                                   label in self._mappings]) + ']'
        additional = {
            'mappings': mappings
        }

        return super().dump('Switch', additional)

    def append(self, element: BaseElement) -> None:
        return
