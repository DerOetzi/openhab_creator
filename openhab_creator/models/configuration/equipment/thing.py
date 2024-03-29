from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from openhab_creator import logger

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment
    from openhab_creator.models.configuration.equipment.bridge import Bridge


class Properties():
    def __init__(self, secrets: Dict[str, str], properties: Dict[str, Any]):
        self._properties: Dict[str, Any] = {}

        for property_key, property_value in properties.items():
            type_hint = None
            if ':' in property_key:
                property_key, type_hint = property_key.split(':')

            if isinstance(property_value, str):
                property_value = property_value.format_map(secrets)

                if type_hint is not None:
                    if type_hint == 'int':
                        property_value = int(property_value)
                    elif type_hint == 'float':
                        property_value = float(property_value)

            self._properties[property_key] = property_value

    @property
    def empty(self) -> bool:
        return len(self.all) == 0

    @property
    def all(self) -> Dict[str, Any]:
        return self._properties

    def has(self, property_key: str) -> bool:
        return property_key in self._properties

    def key(self, property_key: str) -> Any | None:
        property_value = None
        if self.has(property_key):
            property_value = self._properties[property_key]

        return property_value


class Channel():
    def __init__(self,
                 secrets: Dict[str, str],
                 identifier: str,
                 typed: str,
                 name: str,
                 properties: Dict[str, Any]):
        self.identifier: str = identifier
        self.typed: str = typed
        self.name: str = name
        self._properties: Properties = Properties(secrets, properties)

    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties.all


class Thing():
    def __init__(self,
                 equipment_node: Equipment,
                 thingtype: str,
                 thinguid: Optional[str] = None,
                 configuration: Optional[Configuration] = None,
                 secrets_config: Optional[List[str]] = None,
                 nameprefix: Optional[str] = '',
                 properties: Optional[Dict[str, Any]] = None,
                 channels: Optional[Dict[str, Any]] = None,
                 bridge: Optional[str] = None,
                 mac: Optional[bool] = False,
                 asbridge: Optional[str] = None):

        self.equipment_node: Equipment = equipment_node

        self.typed: str = thingtype

        self._init_bridge(configuration, bridge, asbridge)

        self._init_nameprefix(nameprefix)

        self._init_binding()

        self._init_secrets(configuration, secrets_config or [])

        self.uid: str = equipment_node.identifier if thinguid is None else self.replace_secrets(
            thinguid)

        self._init_channelprefix()

        self._properties: Properties = Properties(
            self.secrets, properties or {})

        self._init_channels(channels or {})

        self.mac: Optional[str] = configuration.equipment.register_mac(
            self.equipment_node) if mac else None

    def _init_bridge(self,
                     configuration: Optional[Configuration] = None,
                     bridge_key: Optional[str] = None,
                     asbridge: Optional[str] = None) -> None:

        self.bridge: Optional[Bridge] = None
        self.same_bridge = None

        if not (configuration is None or bridge_key is None):
            self.bridge = configuration.equipment.bridge(bridge_key)
            self.bridge.add_thing(self)

            if asbridge is not None:
                self.same_bridge = configuration.equipment.bridge(asbridge)
                self.same_bridge.parent_bridge = self.bridge
                self.same_bridge.thing = self

    @property
    def is_subbridge(self) -> bool:
        return self.same_bridge is not None

    def _init_nameprefix(self, nameprefix: str) -> None:
        if self.has_bridge and self.bridge.is_thing:
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

        if self.equipment_node.has_person:
            self.secrets['person'] = self.equipment_node.person.name

        prefixes = [
            self.binding,
            self.equipment_node.category,
            self.equipment_node.identifier
        ]

        for secret_key in secrets_config:
            self.secrets[secret_key] = configuration.secrets.secret(
                *prefixes, secret_key)

        logger.debug('secrets: %s', self.secrets)

    def _init_channelprefix(self) -> None:
        prefixes = [
            self.binding,
            self.typed
        ]

        if self.has_bridge:
            if self.bridge.is_subbridge \
                    and self.bridge.parent_bridge.is_thing:
                prefixes.append(self.bridge.parent_bridge.thing.uid)

            if self.bridge.is_thing \
                    and self.bridge.identifier != self.equipment_node.identifier:

                prefixes.append(self.bridge.thing.uid)

        prefixes.append(self.uid)

        self.channelprefix: str = ':'.join(prefixes)

    def _init_channels(self, channels: Dict[str, Any]) -> None:
        self._channels: Dict[str, Channel] = {}

        for channel_key, channel_definition in channels.items():
            self._channels[channel_key] = Channel(
                self.secrets, channel_key, **channel_definition)

    @property
    def channels(self) -> List[Channel]:
        return self._channels.values()
    
    def channel(self, channel_key: str) -> Channel | None:
        channel = None
        if channel_key in self._channels:
            channel = self._channels[channel_key]

        return channel
    
    def channel_unit(self, channel_key: str, fallback:str) -> str:
        unit = fallback
        channel = self.channel(channel_key)
        if channel is not None and 'unit' in channel.properties:
            unit = channel.properties['unit']

        return unit

    def has_point(self, point: str) -> bool:
        return point in self._channels

    def replace_secrets(self, input_str: str) -> str:
        return input_str.format_map(self.secrets)

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

    def has_property(self, property_key: str) -> bool:
        return self._properties.has(property_key)

    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties.all

    @property
    def has_channels(self) -> bool:
        return len(self.channels) > 0

    @property
    def has_mac(self) -> bool:
        return self.mac is not None
