from .secrets import SecretRegistry

class Bridge(object):
    @staticmethod
    def bridgeprops():
        raise Exception('Not implemented interface method')

    @staticmethod
    def thingstring(thing):
        return ''
        #TODO raise Exception('Not implemented interface method')

class AVMBridge(Bridge):
    @staticmethod
    def bridgeprops():
        return {
            "thingtype": "avmfritz:fritzbox:%s" % SecretRegistry.secret('fritzbox', 'id'),
            "name": "Fritz.Box",
            "properties": {
                "ipAddress": SecretRegistry.secret('fritzbox', 'ip'),
                "password": SecretRegistry.secret('fritzbox', 'password')
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
    def thingstring(thing):
        typed = thing.typed()
        subtype = thing.attr('subtype')

        return u'{thingtype} {ain} "Fritz.Box {typed} {name}" @ "{typed}" [ ain="{ain}" ]'.format(
            thingtype = AVMBridge.THING_TYPES[typed][subtype],
            typed = typed, name = thing.name(),
            ain = SecretRegistry.secret('fritzbox', typed, thing.id(), 'ain')
        )

class DeconzBridge(Bridge):
    @staticmethod
    def bridgeprops():
        return {
            "thingtype": 'deconz:deconz:homeserver',
            "name": 'Deconz',
            "properties": {
                "host": SecretRegistry.secret('deconz', 'host'),
                "apikey": SecretRegistry.secret('deconz', 'apikey')
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
        'rgb': {
            'thing': 'extendedcolorlight',
            'uidsuffix': '0b',
            'nameprefix': 'RGB',
            'category': 'controls'
        }
    }

    @staticmethod
    def thingstring(thing):
        typed = thing.typed()
        subtype = thing.attr('subtype', '')
        if typed == 'airsensor' and subtype == 'aqara':
            return u"""temperaturesensor {uid}010402 \"Deconz Airsensor temperature {name}\" @ \"sensors\" [id=\"{temperature_id}\"]
Thing humiditysensor {uid}010405 \"Deconz Airsensor humidity {name}\" @ \"sensors\" [id=\"{humidity_id}\"]
Thing pressuresensor {uid}010403 \"Deconz Airsensor pressure {name}\" @ \"sensors\" [id=\"{pressure_id}\"]""".format(
                    uid=SecretRegistry.secret('deconz', 'aqara', thing.id(), 'uid'),
                    name=thing.name(),
                    temperature_id=SecretRegistry.secret('deconz', 'aqara', thing.id(), 'temperature', 'id'),
                    humidity_id=SecretRegistry.secret('deconz', 'aqara', thing.id(), 'humidity', 'id'),
                    pressure_id=SecretRegistry.secret('deconz', 'aqara', thing.id(), 'pressure', 'id'),
                )
        else:
            thingDef = DeconzBridge.THING_TYPES[typed]
            return u'{thingType} {uid}{suffix} "Deconz {prefix} {name}" @ "{category}" [id="{id}"]'.format(
                thingType=thingDef['thing'],
                uid = SecretRegistry.secret('deconz', typed, thing.id(), 'uid'),
                suffix = thingDef['uidsuffix'],
                prefix = thingDef['nameprefix'],
                name = thing.name(),
                category = thingDef['category'],
                id = SecretRegistry.secret('deconz', typed, thing.id(), 'id')
            )

class MQTTBridge(Bridge):
    @staticmethod
    def bridgeprops():
        return {
            "thingtype": 'mqtt:broker:local',
            "name": 'MQTT Broker local',
            "properties": {
                "host": SecretRegistry.secret('mqtt', 'host'),
                "secure": False,
                "clientID": "openHAB",
                "username": "openhab",
                "password": SecretRegistry.secret('mqtt', 'password')
            }
        }
    
class NetatmoBridge(Bridge):
    @staticmethod
    def bridgeprops():
        return {
            "thingtype": "netatmo:netatmoapi",
            "name": "Netatmo Bridge",
            "properties": {
                "clientId": SecretRegistry.secret('netatmo', 'clientId'),
                "clientSecret": SecretRegistry.secret('netatmo', 'clientSecret'),
                "username": SecretRegistry.secret('netatmo', 'username'),
                "password": SecretRegistry.secret('netatmo', 'password'),
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