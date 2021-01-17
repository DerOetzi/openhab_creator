from __future__ import annotations

import os
from typing import Dict

from openhab_creator.models.configuration import SmarthomeConfiguration
from openhab_creator.models.thing.basething import BaseThing
from openhab_creator.models.thing.bridge import Bridge
from openhab_creator.models.thing.equipment.equipment import Equipment
from openhab_creator.output.basecreator import BaseCreator


class ThingsCreator(BaseCreator):
    def __init__(self, outputdir: str, check_only: bool):
        super().__init__('things', outputdir, check_only)

    def build(self, configuration: SmarthomeConfiguration) -> None:
        for bridge_key, bridge_obj in configuration.bridges().items():
            self.__append_bridge(bridge_obj)
            for thing in bridge_obj.things():
                self.__append_thing(thing)

            self._append('}')

            self._write_file(bridge_key)

    def __append_bridge(self, bridge: Bridge) -> None:
        bridgestring = 'Bridge {type}:{bridgetype}:{identifier} "{nameprefix} {name} ({identifier})"%s {{'
        bridgestring = bridgestring % self._propertiesstring(
            bridge.properties())
        bridgestring = bridgestring.format_map(bridge.replacements())
        self._append(bridgestring)

    def __append_thing(self, thing: Equipment) -> None:
        thingstring = '  Thing {thingtype} {thinguid} "{bridgenameprefix} {nameprefix} {name} ({identifier})" @ "{type}"%s%s'
        thingstring = thingstring % (
            self._propertiesstring(thing.properties()),
            self._channelsstring(thing)
        )
        thingstring = thingstring.format_map(thing.replacements())
        self._append(thingstring)

    def _propertiesstring(self, properties: Dict[str, str]) -> str:
        if len(properties) == 0:
            return ''

        properties_pairs = []

        for (key, value) in properties.items():
            if type(value) is int:
                properties_pairs.append('%s=%d' % (key, value))
            elif type(value) is bool:
                properties_pairs.append('%s=%s' % (
                    key, 'true' if value else 'false'))
            else:
                properties_pairs.append('%s="%s"' % (key, value))

        return ' [%s]' % (', '.join(properties_pairs))

    def _channelsstring(self, thing: Equipment) -> str:
        if not thing.has_channels():
            return ''

        lines = []
        lines.append('{{')
        lines.append('    Channels:')

        for channel in thing.channels():
            lines.append('      Type %s : %s "%s"%s' % (
                channel['type'], channel['id'], channel['name'],
                self._propertiesstring(channel['properties'])
            ))
        lines.append('  }}')

        return "\n".join(lines)
