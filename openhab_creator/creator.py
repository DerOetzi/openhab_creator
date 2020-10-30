from . import __version__
from .model import Floor, Room, Device

import json

class Creator(object):
    def __init__(self, configfile, outputdir):
        self.configjson = json.load(configfile)
        self.outputdir = outputdir
        
        self.floors = []
        self.rooms = []
        self.devices = []

    def run(self):
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self.outputdir)
        
        self.parse()

    def parse(self):
        for location in self.configjson.values():
            self._parseFloors(location)

        print(self.floors)
        print(self.rooms)
        print(self.devices)

    def _parseFloors(self, location):
        if 'floors' in location:
            for floor in location['floors']:
                floorObj = Floor(floor)
                self.floors.append(floorObj)
                self._parseDevices(floor, floorObj)
                self._parseRooms(floor, floorObj)

    def _parseRooms(self, floor, floorObj):
        if 'rooms' in floor:
            for room in floor['rooms']:
                roomObj = Room(room, floorObj)
                self.rooms.append(roomObj)
                self._parseDevices(room, floorObj, roomObj)

    def _parseDevices(self, parentObj, floorObj, roomObj = None):
        if 'devices' in parentObj:
            for device in parentObj['devices']:
                deviceObj = Device(device, floorObj, roomObj)
                self.devices.append(deviceObj)
