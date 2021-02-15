from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional

from openhab_creator import logger

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment
    from openhab_creator.models.configuration.equipment.bridge import Bridge


class Properties(object):
    def __init__(self, secrets: Dict[str, str], properties: Dict[str, Any]):
        self._properties: Dict[str, Any] = {}

        for property_key, property_value in properties.items():
            if isinstance(property_value, str):
                property_value = property_value.format_map(secrets)

            self._properties[property_key] = property_value

    @property
    def empty(self) -> bool:
        return len(self.all) == 0

    @property
    def all(self) -> Dict[str, Any]:
        return self._properties


class Channel(object):
    def __init__(self, secrets: Dict[str, str], identifier: str, typed: str, name: str, properties: Dict[str, Any]):
        self.identifier: str = identifier
        self.typed: str = typed
        self.name: str = name
        self._properties: Properties = Properties(secrets, properties)

    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties.all


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

        self.equipment_node: Equipment = equipment_node

        self.typed: str = thingtype

        self._init_bridge(configuration, bridge)

        self._init_nameprefix(nameprefix)

        self._init_binding()

        self._init_secrets(
            configuration, [] if secrets_config is None else secrets_config)

        self.uid: str = equipment_node.identifier if thinguid is None else self.replace_secrets(
            thinguid)

        self._init_channelprefix()

        self._properties: Properties = Properties(
            self.secrets, {} if properties is None else properties)

        self._init_channels({} if channels is None else channels)

    def _init_bridge(self,
                     configuration: Optional[Configuration] = None,
                     bridge_key: Optional[str] = None) -> None:

        self.bridge: Optional[Bridge] = None

        if not (configuration is None or bridge_key is None):
            self.bridge = configuration.bridge(bridge_key)
            self.bridge.add_thing(self)

    def _init_nameprefix(self, nameprefix: str) -> None:
        if self.has_bridge:
            nameprefix = f'{self.bridge.thing.nameprefix} {nameprefix}'

        self.nameprefix: str = nameprefix

    def _init_binding(self) -> None:
        if self.has_bridge:
            binding = self.bridge.binding
        elif hasattr(self.equipment_node, 'binding'):
            binding = self.equipment_node.binding

        self.binding: str = binding

    def _init_secrets(self, configuration: Configuration, secrets_config: List[str]) -> None:
        self.secrets: Dict[str, str] = {
            'identifier': self.equipment_node.identifier
        }

        prefixes = [
            self.binding,
            self.equipment_node.category,
            self.equipment_node.identifier
        ]

        for secret_key in secrets_config:
            self.secrets[secret_key] = configuration.secrets.secret(
                *prefixes, secret_key)

        logger.debug(f'secrets: {self.secrets}')

    def _init_channelprefix(self) -> None:
        prefixes = [
            self.binding,
            self.typed
        ]

        if self.has_bridge:
            prefixes.append(self.bridge.thing.uid)

        prefixes.append(self.uid)

        self.channelprefix: str = ':'.join(prefixes)

    def _init_channels(self, channels: Dict[str, Any]) -> None:
        self.channels: List[Channel] = []

        for channel_key, channel_definition in channels.items():
            self.channels.append(
                Channel(self.secrets, channel_key, **channel_definition))

        logger.debug(f'channels: {self.channels}')

    def replace_secrets(self, input: str) -> str:
        return input.format_map(self.secrets)

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
    def has_bridge(self) -> bool:
        return self.bridge is not None

    @property
    def has_properties(self) -> bool:
        return not self._properties.empty

    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties.all

    @property
    def has_channels(self) -> bool:
        return len(self.channels) > 0
