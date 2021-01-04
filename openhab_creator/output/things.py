import os
from openhab_creator.model import Thing, Bridge

class ThingsCreator:
    def __init__(self, outputdir):
        self._outputdir = '%s/things' % outputdir

    def build(self, bridges, checkOnly = False):
        for bridgeKey, bridgeObj in bridges.items():
            lines = []
            lines.append(self._bridgestring(bridgeObj))
            # for thing in bridgeObj.things():
            #     thingReplacements = thing.replacements()
            #     channels = []
            #     if thing.hasChannels():
            #         channels.append('{')
            #         for channel in thing.channels():
            #             channels.append('    Type %s : %s "%s" %s' % (
            #                 channel['type'], channel['id'], channel['name'],
            #                 self._propertiesstring(channel, thingReplacements)
            #             )) 
            #         channels.append('  }')

            #     lines.append(u'  Thing %s %s' % (thing.thingdef(), "\n".join(channels)))

            lines.append('}')

            if not checkOnly:
                self._writeFile(bridgeKey, lines)

    def _bridgestring(self, bridge: Bridge):
        bridgestring = 'Bridge {type}:{bridgetype}:{id} "{nameprefix} {name} ({id})"%s {{'
        bridgestring = bridgestring % self._propertiesstring(bridge.properties())
        return bridgestring.format_map(bridge.replacements())

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

    def _writeFile(self, bridgeKey, lines: list):
        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)

        with open('%s/%s.things' % (self._outputdir, bridgeKey), 'w') as f:
            f.writelines("\n".join(lines))

