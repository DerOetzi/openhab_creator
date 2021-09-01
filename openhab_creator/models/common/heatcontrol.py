from __future__ import annotations

from typing import Dict, List, Tuple

from openhab_creator import CreatorEnum, _
from openhab_creator.output.color import Color


class Heatcontrol(CreatorEnum):
    COMFORT = 'COMFORT', _('Comfort'), Color.YELLOW
    ECO = 'ECO', _('ECO'), Color.GREEN
    CLOSED = 'CLOSED', _('Closed'), Color.LIGHTGREY
    BOOST = 'BOOST', _('Boost'), Color.RED

    def __init__(self, identifier: str, label: str, color: Color):
        self.identifier: str = identifier
        self.label: str = label
        self.color: Color = color

    @classmethod
    def colors(cls, item: str) -> List[Tuple[str, Color]]:
        return list(map(lambda x: (f'{item}=="{x.identifier}"', x.color), cls))

    @classmethod
    def mappings(cls) -> Dict[str, str]:
        return dict(map(lambda x: (x.identifier, x.label), cls))

    @classmethod
    def switch_mappings(cls, with_boost: bool) -> List[Tuple[str, str]]:
        if with_boost:
            controls = cls
        else:
            controls = filter(lambda x: x.identifier != 'BOOST', cls)

        return list(map(lambda x: (x.identifier, x.label), controls))
