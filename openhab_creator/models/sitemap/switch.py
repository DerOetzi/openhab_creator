from __future__ import annotations

from typing import Any, List, Optional, Tuple

from openhab_creator import _
from openhab_creator.output.formatter import Formatter
from openhab_creator.models.sitemap.baseelement import BaseElement


class Switch(BaseElement):
    def __init__(self,
                 item: str,
                 mappings: List[Tuple[str, str]],
                 label: Optional[str] = ''):
        super().__init__(item, label)

        self.attribute(
            'mappings',
            Formatter.key_value_tuples(mappings, separator=",\n            "),
            '[', ']')

    @property
    def elementtype(self) -> str:
        return 'Switch'


class Selection(Switch):
    @property
    def elementtype(self) -> str:
        return 'Selection'


class ActiveSwitch(Switch):
    def __init__(self,
                 item: str,
                 label: Optional[str] = ''):
        super().__init__(item, [
            ('OFF', _('Inactive')),
            ('ON', _('Active'))
        ], label)


class AutomationSwitch(Switch):
    def __init__(self,
                 item: str,
                 with_off: Optional[bool] = False,
                 label: Optional[str] = ''):
        mappings = []

        if with_off:
            mappings.append(('OFF', _('Off')))

        mappings.append(('ON', _('Automation')))

        super().__init__(item, mappings, label)


class OnOffSwitch(Switch):
    def __init__(self,
                 item: str,
                 label: Optional[str] = '') -> Any:

        super().__init__(item,
                         [('OFF', _('Off')), ('ON', _('On'))],
                         label)
