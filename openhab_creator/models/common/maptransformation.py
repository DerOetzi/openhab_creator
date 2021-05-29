from __future__ import annotations

from typing import Dict

from openhab_creator import _, CreatorEnum
from openhab_creator.models.common.scene import Scene
from openhab_creator.models.common.presence import Presence
from openhab_creator.models.common.weathercondition import WeatherCondition


class MapTransformation(CreatorEnum):
    ACTIVE = "active", {
        'OFF': _('Inactive'), 'ON': _('Active')
    }

    LOWBATTERY = "lowbattery", {
        '0': _('Ok'), '1': _('Low'),
        'OFF': _('Ok'), 'ON': _('Low')
    }

    ONLINE = "online", {'ON': _('Online'), 'OFF': _('Offline')}

    PRESENCE = "presence", Presence.mappings

    SCENE = "scene", Scene.mappings

    TREND = "trend", {
        'falling': _('Falling'),
        'consistent': _('Consistent'),
        'rising': _('Rising')
    }

    WEATHERCONDITION = "weathercondition", WeatherCondition.mappings

    def __init__(self, filename: str, mappings: Dict[str, str]):
        self.filename: str = filename
        self.mappings: Dict[str, str] = mappings

    @ property
    def formatstr(self) -> str:
        return f'MAP({self.filename}.map):%s'
