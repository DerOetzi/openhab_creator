from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator.models.sitemap.baseelement import BaseElement


class Switch(BaseElement):
    def __init__(self, **args):
        self._mappings: Dict[str, str] = args.pop('mappings')

        super().__init__(**args)

    def dump(self) -> str:
        mappings = '[' + ",".join([f'{command}={label}' for command,
                                   label in self._mappings.items()]) + ']'
        additional = {
            'mappings': mappings
        }

        return super().dump('Switch', additional)

    def append(self, element: BaseElement) -> None:
        return
