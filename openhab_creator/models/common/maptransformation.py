from __future__ import annotations

from typing import Dict

from openhab_creator import CreatorEnum, _
from openhab_creator.models.common.presence import Presence
from openhab_creator.models.common.scene import Scene
from openhab_creator.models.common.weatherstation import (DWDEvent,
                                                          DWDSeverity,
                                                          WeatherCondition)
from openhab_creator.models.common.heatcontrol import Heatcontrol
from openhab_creator.models.common.pollencountindex import PollenCountIndex


class MapTransformation(CreatorEnum):
    ONOFF = 'onoff', {
        'OFF': _('Off'), 'ON': _('On')
    }

    ACTIVE = "active", {
        'OFF': _('Inactive'), 'ON': _('Active')
    }

    CALLSTATE = "callstate", {
        'IDLE': _('Inactive'),
        'RINGING': _('Ringing'),
        'DIALING': _('Dialing'),
        'ACTIVE': _('Active')
    }

    DARKNESS = "darkness", {
        'OFF': _('Bright'), 'ON': _('Dark')
    }

    HEATING = "heating", {
        'OFF': _('Inactive'), 'ON': _('Active')
    }

    LOWBATTERY = "lowbattery", {
        '0': _('Ok'), '1': _('Low'),
        'OFF': _('Ok'), 'ON': _('Low')
    }

    ONLINE = "online", {'ON': _('Online'), 'OFF': _('Offline')}

    WINDOWOPEN = "windowopen", {'OPEN': _('Opened'), 'CLOSED': _('Closed')}

    POLLENCOUNT_API = 'pollencountapi', PollenCountIndex.api_mappings()

    POLLENCOUNT = 'pollencount', PollenCountIndex.mappings()

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

    WHITEGOOD_STATE = 'whitegoodstate', {
        'OFF': _('Off'),
        'RUNNING': _('Running'),
        'READY': _('Ready'),
        'STANDBY': _('Standby')
    }

    HEATCONTROL = 'heatcontrol', Heatcontrol.mappings()

    STATION_OPEN = 'stationopen', {
        'OPEN': _('Opened'),
        'CLOSED': _('Closed')
    }

    def __init__(self, filename: str, mappings: Dict[str, str]):
        self.filename: str = filename
        self.mappings: Dict[str, str] = mappings

    @ property
    def formatstr(self) -> str:
        return f'MAP({self.filename}.map):%s'
