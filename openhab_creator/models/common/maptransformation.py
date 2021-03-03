from __future__ import annotations

from typing import Dict

from openhab_creator import _, CreatorEnum
from openhab_creator.models.common.scene import Scene


class MapTransformation(CreatorEnum):
    ACTIVE = "active", {
        'OFF': _('Inactive'), 'ON': _('Active')
    }

    LOWBATTERY = "lowbattery", {
        '0': _('Ok'), '1': _('Low'),
        'OFF': _('Ok'), 'ON': _('Low')
    }

    SCENE = "scene", Scene.mappings

    def __init__(self, filename: str, mappings: Dict[str, str]):
        self.filename: str = filename
        self.mappings: Dict[str, str] = mappings

    @property
    def formatstr(self) -> str:
        return f'MAP({self.filename}.map):%s'
