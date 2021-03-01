from __future__ import annotations

from typing import Dict

from openhab_creator import _, CreatorEnum


class MapTransformation(CreatorEnum):
    ACTIVE = "active", {
        'OFF': _('Inactive'),
        'ON': _('Active')
    }

    LOWBATTERY = "lowbattery", {
        '0': _('Ok'),
        '1': _('Low'),
        'OFF': _('Ok'),
        'ON': _('Low')
    }

    def __init__(self, filename: str, mappings: Dict[str, str]):
        self.filename: str = filename
        self.mappings: Dict[str, str] = mappings
