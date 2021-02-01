from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional

from openhab_creator import logger

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment
    from openhab_creator.models.configuration.equipment.bridge import Bridge


class Properties(object):
    def __init__(self, secrets: Dict[str, str], properties: Dict[str, Any]):
        self.__PROPERTIES: Final[Dict[str, Any]] = {}

        for property_key, property_value in properties.items():
            if isinstance(property_value, str):
                property_value = property_value.format_map(secrets)

            self.__PROPERTIES[property_key] = property_value

    @property
    def empty(self) -> bool:
        return len(self.all) == 0

    @property
    def all(self) -> Dict[str, Any]:
        return self.__PROPERTIES


class Channel(object):
    def __init__(self, secrets: Dict[str, str], identifier: str, typed: str, name: str, properties: Dict[str, Any]):
        self.__IDENTIFIER: Final[str] = identifier
        self.__TYPED: Final[str] = typed
        self.__NAME: Final[str] = name
        self.__PROPERTIES: Final[Properties] = Properties(secrets, properties)

    @property
    def identifier(self) -> str:
        return self.__IDENTIFIER

    @property
    def typed(self) -> str:
        return self.__TYPED

    @property
    def name(self) -> str:
        return self.__NAME

    @property
    def properties(self) -> Dict[str, Any]:
        return self.__PROPERTIES.all


class Thing(object):
    def __init__(self,
                 equipment_node: Equipment,
                 thingtype: str,
                 thinguid: Optional[str] = None,
                 configuration: Optional[Configuration] = None,
                 secrets_config: Optional[List[str]] = None,
                 nameprefix: Optional[str] = '',
                 properties: Optional[Dict[str, Any]] = None,
                 channels: Optional[Dict[str, Any]] = None,
                 bridge: Optional[str] = None):

        self.__EQUIPMENT_NODE: Final[Equipment] = equipment_node

        self.__THINGTYPE: Final[str] = thingtype

        self.__init_bridge(configuration, bridge)

        self.__init_nameprefix(nameprefix)

        self.__init_binding()

        self.__init_secrets(
            configuration, [] if secrets_config is None else secrets_config)

        self.__THINGUID: Final[str] = equipment_node.identifier if thinguid is None else self.__replace_secrets(
            thinguid)

        self.__init_channelprefix()

        self.__PROPERTIES = Properties(
            self.secrets, {} if properties is None else properties)

        self.__init_channels({} if channels is None else channels)

    def __init_bridge(self,
                      configuration: Optional[Configuration] = None,
                      bridge_key: Optional[str] = None) -> None:

        bridge = None

        if not (configuration is None or bridge_key is None):
            bridge = configuration.bridge(bridge_key)
            bridge.add_thing(self)

        self.__BRIDGE: Final[Bridge] = bridge

    def __init_nameprefix(self, nameprefix: str) -> None:
        if self.has_bridge:
            nameprefix = f'{self.bridge.thing.nameprefix} {nameprefix}'

        self.__NAMEPREFIX: Final[str] = nameprefix

    def __init_binding(self) -> None:
        if self.has_bridge:
            binding = self.bridge.binding
        elif hasattr(self.equipment_node, 'binding'):
            binding = self.equipment_node.binding

        self.__BINDING: Final[str] = binding

    def __init_secrets(self, configuration: Configuration, secrets_config: List[str]) -> None:
        self.__SECRETS: Final[Dict[str, str]] = {
            'identifier': self.equipment_node.identifier
        }

        prefixes = [
            self.binding,
            self.equipment_node.category,
            self.equipment_node.identifier
        ]

        for secret_key in secrets_config:
            self.__SECRETS[secret_key] = configuration.secrets.secret(
                *prefixes, secret_key)

        logger.debug(f'secrets: {self.__SECRETS}')

    def __init_channelprefix(self) -> None:
        prefixes = [
            self.binding,
            self.typed
        ]

        if self.has_bridge:
            prefixes.append(self.bridge.thing.uid)

        prefixes.append(self.uid)

        self.__CHANNELPREFIX: Final[str] = ':'.join(prefixes)

    def __init_channels(self, channels: Dict[str, Any]) -> None:
        self.__CHANNELS: Final[List[Any]] = []

        for channel_key, channel_definition in channels.items():
            self.__CHANNELS.append(
                Channel(self.secrets, channel_key, **channel_definition))

        logger.debug(f'channels: {self.channels}')

    def __replace_secrets(self, input: str) -> str:
        return input.format_map(self.secrets)

    @property
    def equipment_node(self) -> Equipment:
        return self.__EQUIPMENT_NODE

    @property
    def nameprefix(self) -> str:
        return self.__NAMEPREFIX

    @property
    def name(self) -> str:
        return self.equipment_node.name

    @property
    def identifier(self) -> str:
        return self.equipment_node.identifier

    @property
    def category(self) -> str:
        return self.equipment_node.category

    @property
    def binding(self) -> str:
        return self.__BINDING

    @property
    def typed(self) -> str:
        return self.__THINGTYPE

    @property
    def uid(self) -> str:
        return self.__THINGUID

    @property
    def bridge(self) -> Bridge:
        return self.__BRIDGE

    @property
    def has_bridge(self) -> bool:
        return self.__BRIDGE is not None

    @property
    def secrets(self) -> Dict[str, str]:
        return self.__SECRETS

    @property
    def has_properties(self) -> bool:
        return not self.__PROPERTIES.empty

    @property
    def properties(self) -> Dict[str, Any]:
        return self.__PROPERTIES.all

    @property
    def has_channels(self) -> bool:
        return len(self.channels) > 0

    @property
    def channels(self) -> List[Any]:
        return self.__CHANNELS

    @property
    def channelprefix(self) -> str:
        return self.__CHANNELPREFIX
