from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Type, Union

from openhab_creator import _
from openhab_creator.exception import BuildException, ConfigurationException
from openhab_creator.models.secretsregistry import SecretsRegistry
from openhab_creator.models.thing.basething import BaseThing
from openhab_creator.output.formatter import Formatter

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.thing.bridge import Bridge
    from openhab_creator.models.location.location import Location


class Equipment(BaseThing):
    def __init__(self,
                 configuration: SmarthomeConfiguration,
                 location: Location,
                 typed: str, name: Optional[str] = '',
                 config: Optional[Dict[str, Union[str, bool]]] = {},
                 identifier: Optional[str] = None,
                 parent: Optional[Equipment] = None,
                 secrets: Optional[List[str]] = [],
                 properties: Optional[Dict] = {},
                 points: Optional[Dict[str, Dict[str, str]]] = {},
                 equipment: Optional[List] = [],
                 channels: Optional[Dict] = {}):

        self. __blankname: str = str(name)
        if identifier is None:
            identifier = location.identifier() + Formatter.format_id(self.__blankname)

        if location is not None:
            name = f'{location.name()} {self.__blankname}'.strip()

        super().__init__(typed, name, identifier, secrets, properties, points)

        self._parent: Optional[Equipment] = parent
        self._location: Optional[Location] = location
        self._subequipment: List[Equipment] = []
        self._channels: List = []

        self._bridge: Bridge = None

        self.__init_subequipment(configuration, equipment, location)
        self.__init_thing(configuration, config, channels)

    def _check_type(self, typed: str, expected: str) -> None:
        if typed.lower() != expected.lower():
            raise BuildException(
                "Tried to parse no {typed} equipment to {self.__class__.__name__}")

    def __init_subequipment(self,
                            configuration: SmarthomeConfiguration,
                            equipment: Dict,
                            location: Location):
        for subequipment in equipment:
            name = f'{self.__blankname} {subequipment["name"]}'.strip()
            subequipment['name'] = name
            self._subequipment.append(
                self.__class__(
                    configuration=configuration,
                    location=location, parent=self, **subequipment))

    def __init_thing(self, configuration: SmarthomeConfiguration, thingconfig: Dict, channels: Dict):
        if self.is_thing():
            self._bridge = configuration.bridge(thingconfig['bridge'])
            self._bridge.append_thing(self)

            self._init_secrets()
            self._init_replacements(thingconfig)
            self._init_channels(channels)

    def _get_secret(self, secret_key: str) -> str:
        return SecretsRegistry.secret(self._bridge.typed(), self._typed, self._identifier, secret_key)

    def _init_replacements(self, thingconfig: Dict) -> None:
        super()._init_replacements()
        self._replacements['binding'] = self._bridge.typed()
        self._replacements['bridgeuid'] = self._bridge.identifier()
        self._replacements['thingtype'] = thingconfig.get('thingtype', '')
        self._replacements['thinguid'] = thingconfig.get(
            'thinguid').format_map(self._replacements)

        self._replacements['bridgenameprefix'] = self._bridge.nameprefix()
        self._replacements['nameprefix'] = thingconfig.get('nameprefix', '')

    def _init_channels(self, channels: Dict) -> None:
        for channel_key, channel_definition in channels.items():
            channel = {
                "type": channel_definition['typed'],
                "id": channel_key,
                "name": channel_definition['name'],
                "properties": deepcopy(channel_definition['properties'])
            }

            self._channels.append(channel)

    def is_thing(self) -> bool:
        return not self.has_subequipment()

    def has_subequipment(self) -> bool:
        return len(self._subequipment) > 0

    def subequipment(self) -> List[Equipment]:
        return self._subequipment

    def parent(self) -> Equipment:
        return self._parent

    def has_parent(self) -> bool:
        return self._parent is not None

    def blankname(self) -> str:
        if self.__blankname == '':
            return self._name

        return self.__blankname

    def location(self) -> Location:
        return self._location

    def toplevel_location(self) -> Location:
        location = self._location

        while location.has_parent():
            location = location.parent()

        return location

    def bridge(self) -> Bridge:
        return self._bridge

    def has_channels(self) -> bool:
        return len(self._channels) > 0

    def channels(self) -> List:
        return self._channels

    def channel(self, point_key: str, point: str) -> str:
        channel_uid = self.point(point_key, point)

        channelstring = f'{{binding}}:{{thingtype}}:{{bridgeuid}}:{{thinguid}}:{channel_uid}'
        return channelstring.format_map(self._replacements)

    def has_battery(self) -> bool:
        return 'battery' in self._points

    def battery_id(self) -> str:
        typed = Formatter.ucfirst(self._typed)
        return f'battery{typed}{self._identifier}'

    def lowbattery_id(self) -> str:
        typed = Formatter.ucfirst(self._typed)
        return f'batteryLow{typed}{self._identifier}'

    def levelbattery_id(self) -> str:
        typed = Formatter.ucfirst(self._typed)
        return f'batteryLevel{typed}{self._identifier}'

    def name_with_type(self):
        return self._name

    def influxdb_tags(self) -> Dict:
        tags = {
            'label': self.name_with_type(),
            'type': self._typed
        }

        return {**tags, **self._location.build_location_tags()}
