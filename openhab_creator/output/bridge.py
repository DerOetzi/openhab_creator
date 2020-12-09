from copy import deepcopy

from .secrets import SecretsRegistry

class Bridge(object):
    @staticmethod
    def bridgeprops():
        raise Exception('Not implemented interface method')

    @staticmethod
    def thingprops(thing):
        return None
        #TODO raise Exception('Not implemented interface method')

class AVMBridge(Bridge):
    BRIDGE_NAME = "Fritz.Box"

    @staticmethod
    def bridgeprops():
        return {
            "thingtype": "avmfritz:fritzbox:%s" % SecretsRegistry.secret('fritzbox', 'id'),
            "name": AVMBridge.BRIDGE_NAME,
            "properties": {
                "ipAddress": SecretsRegistry.secret('fritzbox', 'ip'),
                "password": SecretsRegistry.secret('fritzbox', 'password')
            }
        }

    THING_TYPES = {
        'heating': {
            '301': 'FRITZ_DECT_301',
            'comet': 'Comet_DECT'
        },
        'plug': {
            '210': 'FRITZ_DECT_210'
        }
    }

    @staticmethod
    def thingprops(thing):
        typed = thing.typed()
        subtype = thing.attr('subtype')
        ain = SecretsRegistry.secret('fritzbox', typed, thing.id(), 'ain')
        return {
            "type": AVMBridge.THING_TYPES[typed][subtype],
            "uid": ain,
            "name": u"%s %s %s" % (AVMBridge.BRIDGE_NAME, typed, thing.name()),
            "category": typed,
            "properties": {
                "ain": ain
            }
        }

class DeconzBridge(Bridge):
    @staticmethod
    def bridgeprops():
        return {
            "thingtype": 'deconz:deconz:homeserver',
            "name": 'Deconz',
            "properties": {
                "host": SecretsRegistry.secret('deconz', 'host'),
                "apikey": SecretsRegistry.secret('deconz', 'apikey')
            }
        }
        
    THING_TYPES = {
        'buttons': {
            'thing': 'switch',
            'uidsuffix': '011000',
            'nameprefix': 'Buttons',
            'category': 'controls'
        },
        'colortemperaturelight': {
            'thing': 'colortemperaturelight',
            'uidsuffix': '01',
            'nameprefix': 'Spectrum',
            'category': 'controls'
        },
        'dimmablelight': {
            'thing': 'dimmablelight',
            'uidsuffix': '01',
            'nameprefix': 'Dimmable',
            'category': 'controls'
        },
        'heating': {
            'thing': 'thermostat',
            'uidsuffix': '010201',
            'nameprefix': 'Heating',
            'category': 'heating'
        },
        'humidity': {
            'thing': 'humiditysensor',
            'uidsuffix': '010405',
            'nameprefix': 'Humidity',
            'category': 'sensors'
        },
        'onofflight': {
            'thing': 'onofflight',
            'uidsuffix': '',
            'nameprefix': 'On/Off',
            'category': 'controls'
        },
        'plug': {
            'thing': 'onofflight',
            'uidsuffix': '',
            'nameprefix': 'Plug',
            'category': 'controls'
        },
        'presence': {
            'thing': 'presencesensor',
            'uidsuffix': '010006',
            'nameprefix': 'Presence',
            'category': 'sensors'
        },
        'pressure': {
            'thing': 'pressuresensor',
            'uidsuffix': '010403',
            'nameprefix': 'Pressure',
            'category': 'sensors'
        },
        'rgb': {
            'thing': 'extendedcolorlight',
            'uidsuffix': '0b',
            'nameprefix': 'RGB',
            'category': 'controls'
        },
        'temperature': {
            'thing': 'temperaturesensor',
            'uidsuffix': '010402',
            'nameprefix': 'Temperature',
            'category': 'sensors'
        }
    }

    @staticmethod
    def thingprops(thing):
        typed = thing.typed()
        typeDef = DeconzBridge.THING_TYPES[typed]
        uid = SecretsRegistry.secret('deconz', typed, thing.id(), 'uid').replace(':', '').replace('-', '')
        id = SecretsRegistry.secret('deconz', typed, thing.id(), 'id')
        return {
            "type": typeDef['thing'],
            'uid': "%s%s" % (uid, typeDef['uidsuffix']),
            'name': u"Deconz %s ",
            'category': typeDef['category'],
            'properties': {
                'id': id
            }
        }

class MQTTBridge(Bridge):
    @staticmethod
    def bridgeprops():
        return {
            "thingtype": 'mqtt:broker:local',
            "name": 'MQTT Broker local',
            "properties": {
                "host": SecretsRegistry.secret('mqtt', 'host'),
                "secure": False,
                "clientID": "openHAB",
                "username": "openhab",
                "password": SecretsRegistry.secret('mqtt', 'password')
            }
        }

    THING_TYPES = {
        "rgb": {
            'nameprefix': "WS2812b",
            'category': 'controls',
            'channels': [
                {
                    "type": "string",
                    "uid": "color",
                    "name": "Color",
                    "properties": {
                        "stateTopic": "ws2812b/{}/rgb/state",
                        "commandTopic": "ws2812b/{}/rgb/command"
                    }
                }
            ]
        }
    }

    @staticmethod
    def thingprops(thing):
        typed = thing.typed()

        if typed in MQTTBridge.THING_TYPES:
            typeDef = MQTTBridge.THING_TYPES[typed]
            uid = SecretsRegistry.secret('mqtt', typed, thing.id(), 'uid')
            channels = []
            for channel in deepcopy(typeDef['channels']):
                if 'stateTopic' in channel['properties']:
                    channel['properties']['stateTopic'] = channel['properties']['stateTopic'].format(uid)

                if 'commandTopic' in channel['properties']:
                    channel['properties']['commandTopic'] = channel['properties']['commandTopic'].format(uid)
                
                print(channel)
                channels.append(channel)

            return {
                'type': 'topic',
                'uid': uid,
                'name': 'MQTT %s %s' % (typeDef['nameprefix'], thing.name()),
                'category': typeDef['category'],
                'channels': channels
            }  
        
        return None

class NetatmoBridge(Bridge):
    @staticmethod
    def bridgeprops():
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

class BridgeFactory(object):
    BRIDGES_REGISTRY = {
        "avm": AVMBridge,
        "deconz": DeconzBridge,
        "mqtt": MQTTBridge,
        "netatmo": NetatmoBridge
    }

    @staticmethod
    def bridge(bridge):
        if bridge not in BridgeFactory.BRIDGES_REGISTRY:
            raise Exception('Unknown bridge %s' % bridge)

        return BridgeFactory.BRIDGES_REGISTRY[bridge]