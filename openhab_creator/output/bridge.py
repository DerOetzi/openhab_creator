from copy import deepcopy

import json
import os

from .secrets import SecretsRegistry

class Bridge(object):
    def __init__(self, thingTypes):
        self.THING_TYPES = thingTypes

    def bridgeprops(self):
        raise Exception('Not implemented interface method')

    def thingprops(self, thing):
        raise Exception('Not implemented interface method')

class AVMBridge(Bridge):
    def bridgeprops(self):
        return {
            "thingtype": "avmfritz:fritzbox:%s" % SecretsRegistry.secret('fritzbox', 'id'),
            "name": "Fritz.Box",
            "properties": {
                "ipAddress": SecretsRegistry.secret('fritzbox', 'ip'),
                "user": SecretsRegistry.secret('fritzbox', 'user'),
                "password": SecretsRegistry.secret('fritzbox', 'password')
            }
        }

    def thingprops(self, thing):
        typed = thing.typed()
        subtype = thing.attr('subtype')
        ain = SecretsRegistry.secret('fritzbox', typed, thing.id(), 'ain')
        return {
            "type": self.THING_TYPES[typed][subtype],
            "uid": ain,
            "name": u"%s %s %s" % ("Fritz.Box", typed, thing.name()),
            "category": typed,
            "properties": {
                "ain": ain
            }
        }

class DeconzBridge(Bridge):
    def bridgeprops(self):
        return {
            "thingtype": 'deconz:deconz:homeserver',
            "name": 'Deconz',
            "properties": {
                "host": SecretsRegistry.secret('deconz', 'host'),
                "apikey": SecretsRegistry.secret('deconz', 'apikey')
            }
        }
        
    def thingprops(self, thing):
        typed = thing.typed()
        if typed == "light":
            typed = thing.attr('subtype')
        typeDef = self.THING_TYPES[typed]
        uid = SecretsRegistry.secret('deconz', typed, thing.id(), 'uid').replace(':', '').replace('-', '')
        id = SecretsRegistry.secret('deconz', typed, thing.id(), 'id')
        return {
            "type": typeDef['thing'],
            'uid': "%s%s" % (uid, typeDef['uidsuffix']),
            'name': u"Deconz %s %s" % (typeDef['nameprefix'], thing.name()),
            'category': typeDef['category'],
            'properties': {
                'id': id
            }
        }

class MQTTBridge(Bridge):
    def bridgeprops(self):
        return {
            "thingtype": 'mqtt:broker:local',
            "name": 'MQTT Broker local',
            "properties": {
                "host": SecretsRegistry.secret('mqtt', 'host'),
                "secure": False,
                "clientID": "openHABClient",
                "username": "openhab",
                "password": SecretsRegistry.secret('mqtt', 'password')
            }
        }

    def thingprops(self, thing):
        typed = thing.typed()

        typeDef = self.THING_TYPES[typed]
        uid = SecretsRegistry.secret('mqtt', typed, thing.id(), 'uid')
        channels = []
        for channel in deepcopy(typeDef['channels']):
            if 'stateTopic' in channel['properties']:
                channel['properties']['stateTopic'] = channel['properties']['stateTopic'].format(uid)

            if 'commandTopic' in channel['properties']:
                channel['properties']['commandTopic'] = channel['properties']['commandTopic'].format(uid)
            
            channels.append(channel)

        return {
            'type': 'topic',
            'uid': uid,
            'name': 'MQTT %s %s' % (typeDef['nameprefix'], thing.name()),
            'category': typeDef['category'],
            'channels': channels
        }  
        
class NetatmoBridge(Bridge):
    def bridgeprops(self):
        return {
            "thingtype": "netatmo:netatmoapi:home",
            "name": "Netatmo Bridge",
            "properties": {
                "clientId": SecretsRegistry.secret('netatmo', 'clientId'),
                "clientSecret": SecretsRegistry.secret('netatmo', 'clientSecret'),
                "username": SecretsRegistry.secret('netatmo', 'username'),
                "password": SecretsRegistry.secret('netatmo', 'password'),
                "readStation": True,
                "readHealthyHomeCoach": False,
                "readThermostat": False,
                "readWelcome": False
            }
        }

    def thingprops(self, thing):
        typed = thing.typed()
        subtype = thing.attr('subtype')
        typeDef = self.THING_TYPES[typed][subtype]
        
        mainId = SecretsRegistry.secret('netatmo', typed, subtype)
        properties = {}

        if subtype == 'main':
            properties['id'] = mainId
        else:
            properties['id'] = SecretsRegistry.secret('netatmo', typed, subtype, thing.id())
            properties['parentId'] = mainId

        return {
            "type": typeDef['thing'],
            'uid': "%s" % (properties['id'].replace(':', '')),
            'name': u"Netatmo %s %s" % (typeDef['nameprefix'], thing.name()),
            'category': typeDef['category'],
            'properties': properties
        }

class BridgeFactory(object):
    BRIDGES_REGISTRY = {
        "avm": AVMBridge,
        "deconz": DeconzBridge,
        "mqtt": MQTTBridge,
        "netatmo": NetatmoBridge
    }

    BRIDGES_INSTANCES = {
    }

    @staticmethod
    def bridge(bridge):
        if bridge not in BridgeFactory.BRIDGES_INSTANCES:
            if bridge not in BridgeFactory.BRIDGES_REGISTRY:
                raise Exception('Unknown bridge %s' % bridge)

            path = os.path.dirname(os.path.abspath(__file__))

            with open('%s/templates/things/%s.json' % (path, bridge), 'rb') as f:
                thingTypes = json.load(f)

            BridgeFactory.BRIDGES_INSTANCES[bridge] = BridgeFactory.BRIDGES_REGISTRY[bridge](thingTypes)

        return BridgeFactory.BRIDGES_INSTANCES[bridge]
