from . import __version__
from .model import Floor, Room, Equipment
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
        self._equipment = []

    def run(self):
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self._outputdir)
        
        self.parse()

        if self._secrets is not None:
            SecretsRegistry.init(self._secrets)

        thingsCreator = ThingsCreator(self._outputdir)
        thingsCreator.build(self._equipment, self._checkOnly)

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
                self._parseEquipment(floor, floorObj)
                self._parseRooms(floor, floorObj)

    def _parseRooms(self, floor, floorObj):
        if 'rooms' in floor:
            for room in floor['rooms']:
                roomObj = Room(room, floorObj)
                self._rooms.append(roomObj)
                self._parseEquipment(room, roomObj)

    def _parseEquipment(self, parentObj, location):
        if 'equipment' in parentObj:
            for equipment in parentObj['equipment']:
                equipmentObj = Equipment(equipment, location)
                self._equipment.append(equipmentObj)
