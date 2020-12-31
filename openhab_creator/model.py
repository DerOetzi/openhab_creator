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
        self._devices = []

    def addRoom(self, room):
        self._rooms.append(room)

    def rooms(self):
        return self._rooms

    def floorstring(self):
        return 'Group %s "%s" <%s> ["Floor"]' % (self._id, self._name, self._icon)


class Room(Location):
    VALIDTYPES = [
        "room", 
        "bedroom", 
        "livingroom",
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

        self.devices = []

    def roomstring(self):
        return 'Group %s "%s" <%s> (%s) ["Room","%s"]' % (self._id, self._name, self._icon, self._floor.id(), self._typed)

class Device(BaseObject):
    VALIDTYPES = [
        'light',
        'buttons',
        'presence',
        'rgb',
        'heating',
        'airsensor',
        'soilmoisture',
        'plug',
        'onofflight',
        'colortemperaturelight',
        'dimmablelight',
        'temperature',
        'humidity',
        'pressure'
    ]

    def __init__(self, json, location):
        name = json.get('name', '')
        
        id = location.id() + Formatter.formatId(name)
        name = location.name() + ' ' + name
        
        super().__init__(name.strip(), json, Device.VALIDTYPES, id)

        self._location = location

        self._bridge = json.get('bridge')
        self._json = json

        self._subdevices = []

        if self._typed == 'light' or self._typed == 'rgb':
            bulbs = json.get('bulbs', None)
            count = json.get('count', 0)
            if bulbs is not None:
                for bulb in bulbs:
                    self._subdevices.append(Device(bulb, location))
            else:
                pattern = '{} %d'.format(json.get('name', '')).strip()

                for i in range(1, count + 1):
                    bulb = { 
                        "name": pattern % i,
                        "bridge": self._bridge,
                        "type": json.get('subtype')
                    }
                    self._subdevices.append(Device(bulb, location))
        elif self._typed == 'airsensor' and self.attr('subtype') == 'aqara':
            #TODO Find another solution for deconz specific aqara sensor handling
            self._subdevices.append(Device(
                {
                    "name": "Temperature %s" % (json.get('name', '')),
                    "bridge": self._bridge,
                    "type": "temperature"
                }, location
            ))

            self._subdevices.append(Device(
                {
                    "name": "Humidity %s" % (json.get('name', '')),
                    "bridge": self._bridge,
                    "type": "humidity"
                }, location
            ))

            self._subdevices.append(Device(
                {
                    "name": "Pressure %s" % (json.get('name', '')),
                    "bridge": self._bridge,
                    "type": "pressure"
                }, location
            ))

    def bridge(self):
        return self._bridge

    def hasSubdevices(self):
        return len(self._subdevices) > 0

    def subdevices(self):
        return self._subdevices

    def attr(self, attr, default = None):
        return self._json.get(attr, default)