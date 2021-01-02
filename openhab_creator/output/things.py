import os

class ThingsCreator:
    def __init__(self, outputdir):
        self._outputdir = '%s/things' % outputdir

    def build(self, bridges, checkOnly = False):
        for bridgeKey, bridge in bridges.items():
            lines = []
            lines.append(u'Bridge %s {' % bridge.bridgedef())
            for thing in bridge.things():
                lines.append(u'Thing %s' % thing.thingdef())

            lines.append('}')

            if not checkOnly:
                self._writeFile(bridgeKey, lines)

    def _writeFile(self, bridgeKey, lines: list):
        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)

        with open('%s/%s.things' % (self._outputdir, bridgeKey), 'w') as f:
            f.writelines("\n".join(lines))

