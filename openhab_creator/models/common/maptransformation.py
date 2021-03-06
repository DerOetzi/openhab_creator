from __future__ import annotations

from typing import Dict

from openhab_creator import CreatorEnum, _
from openhab_creator.models.common.presence import Presence
from openhab_creator.models.common.scene import Scene
from openhab_creator.models.common.weatherstation import (DWDEvent,
                                                          DWDSeverity,
                                                          WeatherCondition)


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

    DWDSEVERITY = 'dwdseverity', DWDSeverity.mappings

    DWDEVENT_KEYWORD = 'dwdeventkeyword', DWDEvent.mappings_keyword

    DWDEVENT = 'dwdevent', DWDEvent.mappings_label

    def __init__(self, filename: str, mappings: Dict[str, str]):
        self.filename: str = filename
        self.mappings: Dict[str, str] = mappings

    @ property
    def formatstr(self) -> str:
        return f'MAP({self.filename}.map):%s'
