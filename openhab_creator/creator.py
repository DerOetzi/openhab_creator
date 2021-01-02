from . import __version__
from .model import Floor, Room, Bridge, Equipment
from .output.things import ThingsCreator
from .output.items import ItemsCreator
from .secrets import SecretsRegistry

import json

from copy import deepcopy

class Creator(object):
    def __init__(self, configfile, outputdir, secretsfile, checkOnly):
        self._configjson = json.load(configfile)
        self._outputdir = outputdir
        self._secrets = secretsfile
        self._checkOnly = checkOnly
        
        self._templates = self._configjson['templates']
        
        self._floors = []
        self._bridges = {}
        self._equipment = []

    def run(self):
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self._outputdir)
        
        if self._secrets is not None:
            SecretsRegistry.init(self._secrets)

        self.parse()

        thingsCreator = ThingsCreator(self._outputdir)
        thingsCreator.build(self._bridges, self._checkOnly)

        itemsCreator = ItemsCreator(self._outputdir)
        itemsCreator.buildLocations(self._floors, self._checkOnly)

        if self._secrets is not None:
            SecretsRegistry.handleMissing()

    def parse(self):
        self._parseBridges()

        for location in self._configjson['locations'].values():
            self._parseFloors(location)

    def _parseBridges(self):
        for bridgeKey, bridge in self._configjson['bridges'].items():
            self._bridges[bridgeKey] = Bridge(bridge)

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
                self._parseEquipment(room, roomObj)

    def _parseEquipment(self, parentObj, location):
        if 'equipment' in parentObj:
            for equipment in parentObj['equipment']:
                equipment = self._mergeTemplate(equipment)
                equipmentObj = Equipment(equipment, location)
                self._equipment.append(equipmentObj)
                self._addThingsToBridge(equipmentObj)

    def _mergeTemplate(self, equipment):
        if 'template' in equipment:
            template = self._getTemplateDeepcopy(equipment['template'])
            equipment.pop('template', None)
            for key, value in template.items():
                if key not in equipment:
                    equipment[key] = value

        if 'equipment' in equipment:
            subequipmentNew = []
            for subequipment in equipment['equipment']:
                subequipmentNew.append(self._mergeTemplate(subequipment))

            equipment['equipment'] = subequipmentNew

        return equipment

    def _getTemplateDeepcopy(self, templateName):
        if templateName not in self._templates:
            raise Exception('Template %s not found' % templateName)

        return deepcopy(self._templates[templateName])

    def _addThingsToBridge(self, equipment):
        if equipment.hasSubequipment():
            for subequipment in equipment.subequipment():
                self._addThingsToBridge(subequipment)
        else:
            self._addThingToBridge(equipment)

    def _addThingToBridge(self, thing):
        bridgeKey = thing.bridge()
        if bridgeKey not in self._bridges:
            raise Exception("Bridge %s not known" % bridgeKey)

        self._bridges[bridgeKey].appendThing(thing)
