from copy import deepcopy

from .secrets import SecretsRegistry

class Formatter(object):
    @staticmethod
    def ucfirst(raw):
        if len(raw) > 1:
            return raw[0].upper() + raw[1:].lower()
        elif len(raw) == 1:
            return raw.upper()
        else:
            return ''

    @staticmethod
    def formatId(rawId):
        id = rawId.strip()
        id = id.replace('ö', 'oe')
        id = id.replace('ä', 'ae')
        id = id.replace('ü', 'ue')
        id = id.replace('ß', 'ss')
        id = id.replace(' ', '')
        id = id.replace('_', '')
        return id

class BaseObject(object):
    def __init__(self, name, configuration, validtypes, id = None):
        if id is None:
            id = configuration.get('id', None)
            if id is None:
                id = Formatter.formatId(name)
        
        self._id = Formatter.ucfirst(id)

        self._name = name

        typed = configuration.get('type', None)
        if typed is None:
            self._typed = validtypes[0]
        else:
            typed = typed.lower()
            if typed in validtypes:
                self._typed = typed
            else:
                raise Exception('Invalid type {} for {}'.format(typed, name))

    def id(self):
        return self._id

    def name(self):
        return self._name

    def typed(self):
        return self._typed

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return u'{} ({}, {})'.format(self._name, self._id, self._typed)

class Location(BaseObject):
    pass

class Floor(Location):
    VALIDTYPES = [
        'floor', 
        'attic', 
        'basement', 
        'groundfloor', 
        'firstfloor'
        ]

    def __init__(self, configuration):
        name = configuration.get('name')

        super().__init__(name, configuration, Floor.VALIDTYPES)

        self._icon = configuration.get('icon', None)
        if self._icon is None:
            self._icon = self._typed

        self._rooms = []

    def addRoom(self, room):
        self._rooms.append(room)

    def rooms(self):
        return self._rooms

    def floorstring(self):
        return 'Group %s "%s" <%s> ["Floor", "%s"]' % (self._id, self._name, self._icon, self._typed)


class Room(Location):
    VALIDTYPES = [
        "room", 
        "bedroom", 
        "livingroom",
        "dinningroom",
        "bathroom", 
        "kitchen", 
        "office",
        "corridor"
    ]

    def __init__(self, json, floor):
        name = json.get('name')

        super().__init__(name, json, Room.VALIDTYPES)
        self._icon = json.get('icon', None)
        if self._icon is None:
            self._icon = self._typed

        self._floor = floor
        floor.addRoom(self)

    def roomstring(self):
        return 'Group %s "%s" <%s> (%s) ["Room","%s"]' % (self._id, self._name, self._icon, self._floor.id(), self._typed)

class Thing(BaseObject):
    def __init__(self, name, configuration, validtypes, id = None):
        super().__init__(name, configuration, validtypes, id)
        self._secrets = {}
        self._replacements = {}
        self._properties = configuration['properties'] if 'properties' in configuration else {}

    def _initializeSecrets(self, configuration):
        if 'secrets' in configuration:
            for secretKey in configuration['secrets']:
                self._secrets[secretKey] = self._getSecret(secretKey)

    def _getSecret(self, secretKey):
        raise NotImplementedError("Must override _getSecret")        

    def _initializeReplacements(self):
        self._replacements = {
            "name": self._name,
            "type": self._typed,
            "id": self._id
        }

        for key, value in self._secrets.items():
            self._replacements[key] = value

    def replacements(self):
        return self._replacements

    def properties(self):
        return self._properties

class Bridge(Thing):
    VALIDTYPES = [
        'deconz',
        'mqtt'
    ]

    def __init__(self, configuration):
        name = configuration.get('name')
        super().__init__(name, configuration, Bridge.VALIDTYPES)

        self._things = []

        self._bridgetype = configuration.get('bridgetype')
        self._nameprefix = configuration.get('nameprefix', '')

        self._initializeSecrets(configuration)
        self._initializeReplacements()

    def _getSecret(self, secretKey):
        return SecretsRegistry.secret(self._typed, self._id, secretKey)

    def _initializeReplacements(self):
        super()._initializeReplacements()
        self._replacements['bridgetype'] = self._bridgetype
        self._replacements['nameprefix'] = self._nameprefix

    def bridgetype(self):
        return self._bridgetype

    def nameprefix(self):
        return self._nameprefix

    def appendThing(self, thing):
        self._things.append(thing)
       
    def things(self):
        return self._things

class BridgeManager(object):
    BRIDGE_REGISTRY = {}

    @staticmethod
    def registerBridge(bridgeKey: str, bridge: Bridge):
        BridgeManager.BRIDGE_REGISTRY[bridgeKey] = bridge

    @staticmethod
    def all():
        return BridgeManager.BRIDGE_REGISTRY

    @staticmethod
    def bridge(bridgeKey: str): 
        return BridgeManager.BRIDGE_REGISTRY[bridgeKey]

class Equipment(Thing):
    VALIDTYPES = [
        'lightbulb',
        'sensor'
    ]

    def __init__(self, configuration, location, parent = None):
        name = configuration.get('name', '')
        id = configuration.get('id', None)
        if id is None:
            id = location.id() + Formatter.formatId(name)
        name = location.name() + ' ' + name
        
        super().__init__(name.strip(), configuration, Equipment.VALIDTYPES, id)
        self._parent = None
        self._location = location
        self._subequipment = []
        self._channels = []

        self._bridge = None

        self._initializeSubequiment(configuration)
        self._initializeThing(configuration)
            
    def _initializeSubequiment(self, configuration):
        count = configuration.pop('count', 0)
        if count > 0:
            pattern = '{} %d'.format(configuration.get('name', '')).strip()

            for i in range(1, count + 1):
                subequipment = configuration
                subequipment['name'] = pattern % i
                self._subequipment.append(Equipment(subequipment, self._location, self))
        
        subequipmentList = configuration.pop('equipment', [])
        for subequipment in subequipmentList:
            self._subequipment.append(Equipment(subequipment, self._location, self))

    def _initializeThing(self, configuration):
        if self.isThing():
            self._bridge = BridgeManager.bridge(configuration.get('bridge'))
            self._bridge.appendThing(self)

            self._initializeSecrets(configuration)
            self._initializeReplacements(configuration)
            self._initializeChannels(configuration)

    def isTopLevelGroup(self):
        return self._parent is None

    def isThing(self):
        return not self.hasSubequipment()

    def _getSecret(self, secretKey):
        return SecretsRegistry.secret(self._bridge.typed(), self._typed, self._id, secretKey)
 
    def _initializeReplacements(self, configuration):
        super()._initializeReplacements()
        self._replacements['binding'] = self._bridge.typed()
        self._replacements['thingtype'] = configuration.get('thingtype', '')
        self._replacements['thinguid'] = configuration.get('thinguid').format_map(self._replacements)

        self._replacements['bridgenameprefix'] = self._bridge.nameprefix()
        self._replacements['nameprefix'] = configuration.get('nameprefix', '')
    
    def _initializeChannels(self, configuration):
        if 'channels' in configuration:
            for channelKey, channelDefinition in configuration['channels'].items():
                channel = {
                    "type": channelDefinition['type'],
                    "id": channelKey,
                    "name": channelDefinition['name'],
                    "properties": deepcopy(channelDefinition['properties'])
                }

                self._channels.append(channel)

    def hasSubequipment(self):
        return len(self._subequipment) > 0

    def subequipment(self):
        return self._subequipment

    def bridge(self):
        return self._bridge

    def hasChannels(self):
        return len(self._channels) > 0

    def channels(self):
        return deepcopy(self._channels)