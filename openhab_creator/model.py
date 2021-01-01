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
        return Formatter.ucfirst(id)

class BaseObject(object):
    def __init__(self, name, json, validtypes, id = None):
        if id is None:
            id = json.get('id', None)
            if id is None:
                id = Formatter.formatId(name)
        
        self._id = id

        self._name = name

        typed = json.get('type', None)
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

    def __init__(self, json):
        name = json.get('name')

        super().__init__(name, json, Floor.VALIDTYPES)

        self._icon = json.get('icon', None)
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

class Equipment(BaseObject):
    VALIDTYPES = [
        'lightbulb'
    ]

    def __init__(self, json, location):
        name = json.get('name', '')
        
        id = location.id() + Formatter.formatId(name)
        name = location.name() + ' ' + name
        
        super().__init__(name.strip(), json, Equipment.VALIDTYPES, id)

        self._configuration = deepcopy(json)
        self._bridge = self._configuration.get('bridge')
        self._secrets = {}
        self._location = location
        self._subequipment = []

        count = self._configuration.pop('count', 0)
        if count > 0:
            pattern = '{} %d'.format(json.get('name', '')).strip()

            for i in range(1, count + 1):
                subequipment = deepcopy(self._configuration)
                subequipment['name'] = pattern % i
                self._subequipment.append(Equipment(subequipment, location))
        
        subequipmentList = self._configuration.pop('equipment', [])
        for subequipment in subequipmentList:
            self._subequipment.append(Equipment(subequipment, location))

        if not self.hasSubequipment():
            if 'secrets' in self._configuration:
                for secretKey in self._configuration['secrets']:
                    self._secrets[secretKey] = SecretsRegistry.secret(self._bridge, self._typed, self._id, secretKey)

    def hasSubequipment(self):
        return len(self._subequipment) > 0
