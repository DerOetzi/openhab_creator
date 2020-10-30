class Formatter(object):
    @staticmethod
    def ucfirst(raw):
        return raw[0].upper() + raw[1:].lower()

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
    def __init__(self, name, json, validtypes):
        id = json.get('id', None)
        if id is None:
            self._id = Formatter.formatId(name)
        else:
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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return u'{} ({}, {})'.format(self._name, self._id, self._typed)


class Floor(BaseObject):
    VALID = ['floor', 'attic', 'basement', 'groundfloor', 'firstfloor']

    def __init__(self, json):
        name = json.get('name')

        super().__init__(name, json, Floor.VALID)

        self._icon = json.get('icon', None)

        self._rooms = []
        self._devices = []

    def addRoom(self, room):
        self._rooms.append(room)


class Room(BaseObject):
    VALID = ["room", "bedroom", "livingroom",
             "bathroom", "kitchen", "corridor"]

    def __init__(self, json, floor):
        name = json.get('name')

        super().__init__(name, json, Room.VALID)
        self.icon = json.get('icon', None)

        self.floor = floor
        floor.addRoom(self)

        self.devices = []


class Device(BaseObject):
    VALIDTYPES = [
        'light',
        'buttons',
        'presence',
        'rgb',
        'heating',
        'airsensor',
        'soilmoisture',
        'plug'
    ]

    def __init__(self, json, floorObj, roomObj=None):
        name = json.get('name', None)
        if name is None:
            if roomObj is None:
                name = floorObj.name()
            else:
                name = roomObj.name()

        super().__init__(name, json, Device.VALIDTYPES)
