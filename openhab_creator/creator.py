import json
from typing import List

from copy import deepcopy
from io import BufferedReader, TextIOWrapper

from openhab_creator import __version__

from openhab_creator.secretsregistry import SecretsRegistry

from openhab_creator.models.location import Location
from openhab_creator.models.floor import Floor
from openhab_creator.models.room import Room
from openhab_creator.models.bridge import Bridge
from openhab_creator.models.bridgemanager import BridgeManager
from openhab_creator.models.equipment import Equipment

from openhab_creator.output.thingscreator import ThingsCreator
from openhab_creator.output.itemscreator import ItemsCreator


class Creator(object):
    _configJSON: dict
    _outputdir: str
    _secretsfile: TextIOWrapper
    _checkOnly: bool
    _template: dict

    _bridges: BridgeManager
    _floors: List[Floor] = []
    _equipment: List[Equipment] = []

    def __init__(self, configfile: BufferedReader, outputdir: str, secretsfile: TextIOWrapper, checkOnly: bool):
        self._configjson = json.load(configfile)
        self._outputdir = outputdir
        self._secretsfile = secretsfile
        self._checkOnly = checkOnly

        self._templates = self._configjson['templates']

        self._bridges = BridgeManager()

    def run(self) -> None:
        print("openHAB Configuration Creator (%s)" % __version__)
        print("Output directory: %s" % self._outputdir)

        if self._secretsfile is not None:
            SecretsRegistry.init(self._secretsfile)

        self.parse()

        thingsCreator = ThingsCreator(self._outputdir, self._checkOnly)
        thingsCreator.build(self._bridges)

        itemsCreator = ItemsCreator(self._outputdir)
        itemsCreator.buildLocations(self._floors, self._checkOnly)

        if self._secretsfile is not None:
            SecretsRegistry.handleMissing()

    def parse(self) -> None:
        self._parseBridges()

        for location in self._configjson['locations'].values():
            self._parseFloors(location)

    def _parseBridges(self) -> None:
        for bridgeKey, bridge in self._configjson['bridges'].items():
            self._bridges.register(bridgeKey, Bridge(bridge))

    def _parseFloors(self, locationConfiguration: dict) -> None:
        if 'floors' in locationConfiguration:
            for floorConfiguration in locationConfiguration['floors']:
                floor = Floor(floorConfiguration)
                self._floors.append(floor)
                self._parseEquipment(floorConfiguration, floor)
                self._parseRooms(floorConfiguration, floor)

    def _parseRooms(self, floorConfiguration: dict, floor: Floor) -> None:
        if 'rooms' in floorConfiguration:
            for roomConfiguration in floorConfiguration['rooms']:
                room = Room(roomConfiguration, floor)
                self._parseEquipment(roomConfiguration, room)

    def _parseEquipment(self, parentConfiguration: dict, location: Location) -> None:
        if 'equipment' in parentConfiguration:
            for equipmentConfiguration in parentConfiguration['equipment']:
                equipmentConfiguration = self._mergeTemplate(
                    equipmentConfiguration)
                equipment = Equipment(
                    equipmentConfiguration, location, self._bridges)
                self._equipment.append(equipment)

    def _mergeTemplate(self, equipmentConfiguration: dict) -> dict:
        if 'template' in equipmentConfiguration:
            template = self._getTemplateDeepcopy(
                equipmentConfiguration['template'])
            equipmentConfiguration.pop('template', None)
            for key, value in template.items():
                if key not in equipmentConfiguration:
                    equipmentConfiguration[key] = value

        if 'equipment' in equipmentConfiguration:
            subequipmentConfigurationMerged = []
            for subequipmentConfiguration in equipmentConfiguration['equipment']:
                subequipmentConfigurationMerged.append(
                    self._mergeTemplate(subequipmentConfiguration))

            equipmentConfiguration['equipment'] = subequipmentConfigurationMerged

        return equipmentConfiguration

    def _getTemplateDeepcopy(self, templateName: str) -> dict:
        if templateName not in self._templates:
            raise Exception('Template %s not found' % templateName)

        return deepcopy(self._templates[templateName])
