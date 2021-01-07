from __future__ import annotations
from typing import List, TYPE_CHECKING

from copy import deepcopy

from openhab_creator.secretsregistry import SecretsRegistry

from openhab_creator.models.formatter import Formatter
from openhab_creator.models.thing import Thing

if TYPE_CHECKING:
    from openhab_creator.models.bridge import BridgeManager
    from openhab_creator.models.location import Location
    from openhab_creator.models.bridge import Bridge


class Equipment(Thing):

    VALIDTYPES = [
        'lightbulb',
        'sensor'
    ]

    _parent: Equipment
    _location: Location
    _subequipment: List
    _channels: List
    _bridge: Bridge

    def __init__(self, configuration: dict, location: Location, bridges: BridgeManager, parent: Equipment = None):
        name = configuration.get('name', '')
        config_id = configuration.get('id', None)
        if config_id is None:
            config_id = location.id() + Formatter.format_id(name)
        name = location.name() + ' ' + name

        super().__init__(name.strip(), configuration, Equipment.VALIDTYPES, config_id)
        self._parent = parent
        self._location = location
        self._subequipment = []
        self._channels = []

        self._bridge = None

        self._initializeSubequiment(configuration, bridges)
        self._initializeThing(configuration, bridges)

    def _initializeSubequiment(self, configuration: dict, bridges: BridgeManager) -> None:
        count = configuration.pop('count', 0)
        if count > 0:
            pattern = '{} %d'.format(configuration.get('name', '')).strip()

            for i in range(1, count + 1):
                subequipment = configuration
                subequipment['name'] = pattern % i
                self._subequipment.append(
                    Equipment(subequipment, self._location, bridges, self))

        subequipment_list = configuration.pop('equipment', [])
        for subequipment in subequipment_list:
            self._subequipment.append(
                Equipment(subequipment, self._location, bridges, self))

    def _initializeThing(self, configuration: dict, bridges: BridgeManager) -> None:
        if self.isThing():
            self._bridge = bridges.get(configuration.get('bridge'))
            self._bridge.appendThing(self)

            self._initializeSecrets(configuration)
            self._initializeReplacements(configuration)
            self._initializeChannels(configuration)

    def isTopLevelGroup(self) -> bool:
        return self._parent is None

    def isThing(self) -> bool:
        return not self.hasSubequipment()

    def _getSecret(self, secret_key: str) -> str:
        return SecretsRegistry.secret(self._bridge.typed(), self._typed, self._id, secret_key)

    def _initializeReplacements(self, configuration: dict) -> None:
        super()._initializeReplacements()
        self._replacements['binding'] = self._bridge.typed()
        self._replacements['thingtype'] = configuration.get('thingtype', '')
        self._replacements['thinguid'] = configuration.get(
            'thinguid').format_map(self._replacements)

        self._replacements['bridgenameprefix'] = self._bridge.nameprefix()
        self._replacements['nameprefix'] = configuration.get('nameprefix', '')

    def _initializeChannels(self, configuration: dict) -> None:
        if 'channels' in configuration:
            for channel_key, channel_definition in configuration['channels'].items():
                channel = {
                    "type": channel_definition['type'],
                    "id": channel_key,
                    "name": channel_definition['name'],
                    "properties": deepcopy(channel_definition['properties'])
                }

                self._channels.append(channel)

    def hasSubequipment(self) -> bool:
        return len(self._subequipment) > 0

    def subequipment(self) -> List[Equipment]:
        return self._subequipment

    def bridge(self) -> Bridge:
        return self._bridge

    def hasChannels(self) -> bool:
        return len(self._channels) > 0

    def channels(self) -> List:
        return deepcopy(self._channels)


class EquipmentManager(object):
    __registry: List[Equipment]

    def __init__(self):
        self.__registry = []

    def register(self, equipment: Equipment) -> None:
        self.__registry.append(equipment)

    def all(self):
        return self.__registry
