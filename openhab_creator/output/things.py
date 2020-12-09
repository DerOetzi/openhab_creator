import os

from .bridge import BridgeFactory

class ThingsCreator:
    def __init__(self, outputdir):
        self._outputdir = '%s/things' % outputdir
        self._bridges = {}

    def build(self, devices, checkOnly = False):
        for device in devices:
            if device.hasSubdevices():
                for subdevice in device.subdevices():
                    self._addThingToBridge(subdevice)
            else:
                self._addThingToBridge(device)

        for bridgeKey, bridgeObj in self._bridges.items():
            bridge = bridgeObj['bridge']
            things = bridgeObj['things']

            lines = []
            lines.append(u"%s {" % self._bridgestring(bridge.bridgeprops()))
            for thing in things:
                lines.append("%s" % self._thingstring(bridge.thingprops(thing)))
            lines.append("}")

            if not checkOnly:
                self._writeFile(bridgeKey, lines)

    def _writeFile(self, bridgeKey, lines):
        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)

        with open('%s/%s.things' % (self._outputdir, bridgeKey), 'w') as f:
            f.writelines("\n".join(lines))

    def _addThingToBridge(self, thing):
        bridge = thing.bridge()

        if bridge not in self._bridges:
            self._bridges[bridge] = { 'bridge': BridgeFactory.bridge(bridge), 'things': []}

        self._bridges[bridge]['things'].append(thing) 

    def _bridgestring(self, props):
        properties = self._propertiesstring(props)
        
        return u'Bridge %s "%s" %s' % (props['thingtype'], props['name'], properties)

    def _thingstring(self, props):
        properties = self._propertiesstring(props)
        channels = self._channelsstring(props)

        return u'Thing %s %s "%s" @ "%s"%s%s' % (props['type'], props['uid'], props['name'], props['category'], properties, channels)

    def _channelsstring(self, props):
        if 'channels' not in props:
            return ''

        lines = []
        lines.append("{")
        lines.append("Channels:")
        for channel in props['channels']:
            lines.append(self._channelstring(channel))
        lines.append("}")

        return "\n".join(lines)

    def _channelstring(self, channel):
        properties = self._propertiesstring(channel)
        return 'Type %s : %s "%s" %s' % (channel['type'], channel['uid'], channel['name'], properties)

    def _propertiesstring(self, props):
        if 'properties' not in props:
            return ''

        properties = []

        for (key, value) in props['properties'].items():
            if type(value) is int:
                properties.append('%s=%d' % (key, value))
            elif type(value) is bool:
                properties.append('%s=%s' % (key, 'true' if value else 'false'))
            else:
                properties.append('%s="%s"' % (key, value))

        return ' [%s]' % (', '.join(properties))
        