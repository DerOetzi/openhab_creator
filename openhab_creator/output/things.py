import os

from .bridge import BridgeFactory

class ThingsCreator:
    def __init__(self, outputdir):
        self._outputdir = '%s/things' % outputdir
        self._bridges = {}

    def build(self, devices):
        for device in devices:
            if device.hasSubdevices():
                for subdevice in device.subdevices():
                    self._addThingToBridge(subdevice)
            else:
                self._addThingToBridge(device)

        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)

        for bridgeKey, bridgeObj in self._bridges.items():
            bridge = bridgeObj['bridge']
            things = bridgeObj['things']

            with open('%s/%s.things' % (self._outputdir, bridgeKey), 'w') as f:
                f.write(u"%s {\n" % self._bridgestring(bridge.bridgeprops()))
                for thing in things:
                    f.write("Thing %s\n" % bridge.thingstring(thing))
                f.write("}\n")

    def _addThingToBridge(self, thing):
        bridge = thing.bridge()

        if bridge not in self._bridges:
            self._bridges[bridge] = { 'bridge': BridgeFactory.bridge(bridge), 'things': []}

        self._bridges[bridge]['things'].append(thing) 

    def _bridgestring(self, props):
        properties = ', '.join('{}="{}"'.format(key,val) for (key,val) in props['properties'].items())
        return u'Bridge %s "%s" [%s]' % (props['thingtype'], props['name'], properties)