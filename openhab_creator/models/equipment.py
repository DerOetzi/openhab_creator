from __future__ import annotations
from typing import Dict, List, Type, Literal, TYPE_CHECKING

from copy import deepcopy

from openhab_creator.exception import ConfigurationException, BuildException
from openhab_creator.secretsregistry import SecretsRegistry

from openhab_creator.output.formatter import Formatter
from openhab_creator.models.basething import BaseThing

if TYPE_CHECKING:
    from openhab_creator.models.bridge import BridgeManager
    from openhab_creator.models.location import Location
    from openhab_creator.models.bridge import Bridge

Pointtype = Literal['controls']

class Equipment(BaseThing):

    VALIDTYPES = {
        'lightbulb': 'Lightbulb',
        'sensor': 'Sensor'
    }

    def __init__(self, configuration: dict, location: Location, bridges: BridgeManager, parent: Equipment = None):
        self._blankname: str = configuration.get('name', '')
        config_id = configuration.get('id', None)
        if config_id is None:
            config_id = location.id() + Formatter.format_id(self._blankname)
        name = location.name() + ' ' + self._blankname

        super().__init__(name.strip(), configuration, config_id)
        self._parent: Equipment = parent
        self._configuration: Dict = configuration
        self._location: Location = location
        self._subequipment: List[Equipment] = []
        self._channels: List = []
        self._points: Dict[str, Dict[str, str]] = {}

        self._bridge: Bridge = None

        self._initialize_subequiment(configuration, bridges)
        self._initialize_thing(configuration, bridges)

    def _cast(self, obj: Equipment, newtype: Type) -> None:
        super()._cast(obj)
        self._blankname = obj._blankname
        self._parent = None
        self._configuration = obj._configuration
        self._location = obj._location
        self._channels = obj._channels
        self._points = obj._points
        self._bridge = obj._bridge

        if obj.has_subequipment():
            self._subequipment = []
            for subequipment_old in obj.subequipment():
                subequipment_new = newtype(subequipment_old)
                subequipment_new._parent = self
                self._subequipment.append(subequipment_new)
        else:
            self._subequipment = []

    def _default_type(self) -> str:
        raise ConfigurationException(
            'Equipment always need a type defined in configuration')

    def _is_valid_type(self, typed: str) -> bool:
        return typed in Equipment.VALIDTYPES

    def _initialize_subequiment(self, configuration: dict, bridges: BridgeManager) -> None:
        count = configuration.pop('count', 0)
        if count > 0:
            pattern = f"{configuration.get('name', '')} %d".strip()

            for i in range(1, count + 1):
                subequipment = configuration
                subequipment['name'] = pattern % i
                self._subequipment.append(
                    Equipment(subequipment, self._location, bridges, self))

        subequipment_list = configuration.pop('equipment', [])
        for subequipment in subequipment_list:
            self._subequipment.append(
                Equipment(subequipment, self._location, bridges, self))

    def _initialize_thing(self, configuration: dict, bridges: BridgeManager) -> None:
        if self.is_thing():
            self._bridge = bridges.get(configuration.get('bridge'))
            self._bridge.append_thing(self)

            self._initialize_secrets(configuration)
            self._initialize_replacements(configuration)
            self._initialize_channels(configuration)

            self._points = configuration.get('points', {})

    def parent(self) -> Equipment:
        return self._parent

    def has_parent(self) -> bool:
        return self._parent is not None

    def blankname(self) -> str:
        if self._blankname == '':
            return self._name

        return self._blankname

    def location(self) -> Location:
        return self._location

    def is_thing(self) -> bool:
        return not self.has_subequipment()

    def _get_secret(self, secret_key: str) -> str:
        return SecretsRegistry.secret(self._bridge.typed(), self._typed, self._id, secret_key)

    def _initialize_replacements(self, configuration: dict) -> None:
        super()._initialize_replacements()
        self._replacements['binding'] = self._bridge.typed()
        self._replacements['bridgeuid'] = self._bridge.id()
        self._replacements['thingtype'] = configuration.get('thingtype', '')
        self._replacements['thinguid'] = configuration.get(
            'thinguid').format_map(self._replacements)

        self._replacements['bridgenameprefix'] = self._bridge.nameprefix()
        self._replacements['nameprefix'] = configuration.get('nameprefix', '')

    def _initialize_channels(self, configuration: dict) -> None:
        if 'channels' in configuration:
            for channel_key, channel_definition in configuration['channels'].items():
                channel = {
                    "type": channel_definition['type'],
                    "id": channel_key,
                    "name": channel_definition['name'],
                    "properties": deepcopy(channel_definition['properties'])
                }

                self._channels.append(channel)

    def has_subequipment(self) -> bool:
        return len(self._subequipment) > 0

    def subequipment(self) -> List[Equipment]:
        return self._subequipment

    def bridge(self) -> Bridge:
        return self._bridge

    def has_channels(self) -> bool:
        return len(self._channels) > 0

    def channels(self) -> List:
        return deepcopy(self._channels)

    def points(self, pointtype: Pointtype) -> Dict[str, str]:
        if pointtype in self._points:
            return self._points[pointtype]

        return {}

    def channel(self, pointtype: Pointtype, point: str):
        if pointtype not in self._points:
            raise BuildException(f'Unknown pointtype {pointtype}')

        if point not in self._points[pointtype]:
            raise BuildException(f'Unknown point {point} in {pointtype}')

        channel_uid = self._points[pointtype][point]

        channelstring = f'{{binding}}:{{thingtype}}:{{bridgeuid}}:{{thinguid}}:{channel_uid}'
        return channelstring.format_map(self._replacements)
        


class EquipmentManager(object):
    __registry: Dict[str, List[Equipment]]

    def __init__(self):
        self.__registry = {}

    def register(self, equipment: Equipment) -> None:
        typed = equipment.typed()
        if typed not in self.__registry:
            self.__registry[typed] = []

        self.__registry[typed].append(equipment)

    def all(self) -> Dict[str, List[Equipment]]:
        return self.__registry

    def lightbulbs(self) -> List[Equipment]:
        return self.__registry['lightbulb']
