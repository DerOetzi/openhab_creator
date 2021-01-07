import os

from openhab_creator.models.bridge import Bridge
from openhab_creator.models.bridgemanager import BridgeManager
from openhab_creator.models.equipment import Equipment
from openhab_creator.models.thing import Thing

from openhab_creator.output.basecreator import BaseCreator

class ThingsCreator(BaseCreator):
    def __init__(self, outputdir, check_only):
        super().__init__('things', outputdir, check_only)

    def build(self, bridges: BridgeManager):
        for bridge_key, bridge_obj in bridges.all().items():
            lines = []
            lines.append(self._bridgestring(bridge_obj))
            for thing in bridge_obj.things():
                lines.append(self._thingstring(thing))
            lines.append('}')

            self._write_file(bridge_key, lines)

    def _bridgestring(self, bridge: Bridge):
        bridgestring = 'Bridge {type}:{bridgetype}:{id} "{nameprefix} {name} ({id})"%s {{'
        bridgestring = bridgestring % self._propertiesstring(bridge.properties())
        return bridgestring.format_map(bridge.replacements())

    def _thingstring(self, thing: Equipment):
        thingstring = '  Thing {thingtype} {thinguid} "{bridgenameprefix} {nameprefix} {name} ({id})" @ "{type}"%s%s'
        thingstring = thingstring % (
            self._propertiesstring(thing.properties()),
            self._channelsstring(thing)
        )
        return thingstring.format_map(thing.replacements())

    def _propertiesstring(self, properties):
        if len(properties) == 0:
            return ''

        properties_pairs = []

        for (key, value) in properties.items():
            if type(value) is int:
                properties_pairs.append('%s=%d' % (key, value))
            elif type(value) is bool:
                properties_pairs.append('%s=%s' % (key, 'true' if value else 'false'))
            else:
                properties_pairs.append('%s="%s"' % (key, value))

        return ' [%s]' % (', '.join(properties_pairs))

    def _channelsstring(self, thing: Equipment):
        if not thing.hasChannels():
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

