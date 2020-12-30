from . import __version__
from .model import Floor, Room, Device
from .output.things import ThingsCreator
from .output.items import ItemsCreator
from .output.secrets import SecretsRegistry

import json

class Creator(object):
    def __init__(self, configfile, outputdir, secretsfile, checkOnly):
        self._configjson = json.load(configfile)
        self._outputdir = outputdir
        self._secrets = secretsfile
        self._checkOnly = checkOnly
        
        self._floors = []
        self._rooms = []
        self._devices = []

    def run(self):
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self._outputdir)
        
        self.parse()

        if self._secrets is not None:
            SecretsRegistry.init(self._secrets)

        thingsCreator = ThingsCreator(self._outputdir)
        thingsCreator.build(self._devices, self._checkOnly)

        itemsCreator = ItemsCreator(self._outputdir)
        itemsCreator.buildLocations(self._floors, self._checkOnly)

        if self._secrets is not None:
            SecretsRegistry.handleMissing()

    def parse(self):
        for location in self._configjson.values():
            self._parseFloors(location)

    def _parseFloors(self, location):
        if 'floors' in location:
            for floor in location['floors']:
                floorObj = Floor(floor)
                self._floors.append(floorObj)
                self._parseDevices(floor, floorObj)
                self._parseRooms(floor, floorObj)

    def _parseRooms(self, floor, floorObj):
        if 'rooms' in floor:
            for room in floor['rooms']:
                roomObj = Room(room, floorObj)
                self._rooms.append(roomObj)
                self._parseDevices(room, floorObj, roomObj)

    def _parseDevices(self, parentObj, floorObj, roomObj = None):
        if 'devices' in parentObj:
            for device in parentObj['devices']:
                deviceObj = Device(device, floorObj, roomObj)
                self._devices.append(deviceObj)
