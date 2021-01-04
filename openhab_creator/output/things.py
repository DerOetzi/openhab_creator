import os

class ThingsCreator:
    def __init__(self, outputdir):
        self._outputdir = '%s/things' % outputdir

    def build(self, bridges, checkOnly = False):
        for bridgeKey, bridgeObj in bridges.items():
            bridge = bridgeObj.definition()
            lines = []
            lines.append(u'Bridge %s "%s"%s {' % (
                bridge['type'], bridge['name'],
                self._propertiesstring(bridge, bridgeObj.replacements())
            ))
            for thing in bridgeObj.things():
                thingReplacements = thing.replacements()
                channels = []
                if thing.hasChannels():
                    channels.append('{')
                    for channel in thing.channels():
                        channels.append('    Type %s : %s "%s" %s' % (
                            channel['type'], channel['id'], channel['name'],
                            self._propertiesstring(channel, thingReplacements)
                        )) 
                    channels.append('  }')

                lines.append(u'  Thing %s %s' % (thing.thingdef(), "\n".join(channels)))

            lines.append('}')

            if not checkOnly:
                self._writeFile(bridgeKey, lines)

    def _propertiesstring(self, props, replacements = {}):
        if 'properties' not in props:
            return ''

        properties = []

        for (key, value) in props['properties'].items():
            if type(value) is int:
                properties.append('%s=%d' % (key, value))
            elif type(value) is bool:
                properties.append('%s=%s' % (key, 'true' if value else 'false'))
            else:
                properties.append('%s="%s"' % (key, value.format_map(replacements)))

        return ' [%s]' % (', '.join(properties))

    def _writeFile(self, bridgeKey, lines: list):
        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)

        with open('%s/%s.things' % (self._outputdir, bridgeKey), 'w') as f:
            f.writelines("\n".join(lines))

