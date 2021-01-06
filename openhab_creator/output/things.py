import os
from openhab_creator.model import Thing, Bridge, Equipment

class ThingsCreator:
    def __init__(self, outputdir):
        self._outputdir = '%s/things' % outputdir

    def build(self, bridges, checkOnly = False):
        for bridgeKey, bridgeObj in bridges.items():
            lines = []
            lines.append(self._bridgestring(bridgeObj))
            for thing in bridgeObj.things():
                lines.append(self._thingstring(thing))
            lines.append('}')

            if not checkOnly:
                self._writeFile(bridgeKey, lines)

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

        propertiesPairs = []

        for (key, value) in properties.items():
            if type(value) is int:
                propertiesPairs.append('%s=%d' % (key, value))
            elif type(value) is bool:
                propertiesPairs.append('%s=%s' % (key, 'true' if value else 'false'))
            else:
                propertiesPairs.append('%s="%s"' % (key, value))

        return ' [%s]' % (', '.join(propertiesPairs))

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

    def _writeFile(self, bridgeKey, lines: list):
        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)

        with open('%s/%s.things' % (self._outputdir, bridgeKey), 'w') as f:
            f.writelines("\n".join(lines))

