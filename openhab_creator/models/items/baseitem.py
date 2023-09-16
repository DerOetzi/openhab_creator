from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from openhab_creator import CreatorEnum
from openhab_creator.models.common.maptransformation import BaseMapTransformation
from openhab_creator.models.configuration.baseobject import BaseObject
from openhab_creator.models.configuration.equipment import Equipment
from openhab_creator.output.formatter import Formatter

if TYPE_CHECKING:
    from openhab_creator.models.configuration.location import Location
    from openhab_creator.output.items.baseitemscreator import BaseItemsCreator


class PointType(CreatorEnum):
    ALARM = 'Alarm'
    CONTROL = 'Control'
    SWITCH = 'Switch'
    MEASUREMENT = 'Measurement'
    SETPOINT = 'Setpoint'
    STATUS = 'Status'
    LOWBATTERY = 'LowBattery'
    OPENLEVEL = 'OpenLevel'
    OPENSTATE = 'OpenState'
    TAMPERED = 'Tampered'
    TILT = 'Tilt'


class PropertyType(CreatorEnum):
    TEMPERATURE = 'Temperature'
    LIGHT = 'Light'
    COLORTEMPERATURE = 'ColorTemperature'
    HUMIDITY = 'Humidity'
    PRESENCE = 'Presence'
    PRESSURE = 'Pressure'
    SMOKE = 'Smoke'
    NOISE = 'Noise'
    RAIN = 'Rain'
    WIND = 'Wind'
    WATER = 'Water'
    CO2 = 'CO2'
    CO = 'CO'
    ENERGY = 'Energy'
    POWER = 'Power'
    VOLTAGE = 'Voltage'
    CURRENT = 'Current'
    FREQUENCY = 'Frequency'
    GAS = 'Gas'
    SOUNDVOLUME = 'SoundVolume'
    OIL = 'Oil'
    DURATION = 'Duration'
    LEVEL = 'Level'
    OPENING = 'Opening'
    OZONE = 'Ozone'
    TIMESTAMP = 'Timestamp'
    ULTRAVIOLET = 'Ultraviolet'
    VIBRATION = 'Vibration'


class ProfileType(CreatorEnum):
    JS = 'transform:JS', 'toItemScript'
    MAP = 'transform:MAP', 'function'
    SCALE = 'transform:SCALE', 'function'
    PHONEBOOK = 'transform:PHONEBOOK', 'function'

    def __init__(self, profile: str, function: str) -> None:
        self.profile: str = profile
        self.function: str = function


class AISensorDataType(CreatorEnum):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"


class ExpireType(CreatorEnum):
    STATE = 'state'
    COMMAND = 'command'


class BaseItem():
    influxdb_series = {}
    aisensors = {}
    icons = {}

    def __init__(self, name: str):
        self._name: str = name
        self._label: str = ''
        self._format: Optional[str] = None
        self._icon: Optional[str] = None
        self._groups: List[str] = []
        self._tags: List[str] = []
        self._metadata: Dict[str, Dict] = {}

    @property
    @abstractmethod
    def itemtype(self) -> str:
        pass

    def label(self, label: str) -> BaseItem:
        self._label = label
        return self

    def map(self, mapname: BaseMapTransformation) -> BaseItem:
        return self.format(mapname.formatstr)

    def transform_js(self, js_file: str) -> BaseItem:
        return self.format(f'JS({js_file}.js): %s')

    def format(self, format_string: str) -> BaseItem:
        self._format = format_string
        return self

    def icon(self, icon: str) -> BaseItem:
        self._icon = icon.lower()
        BaseItem.icons[self._icon] = self._icon
        return self

    def groups(self, *groups: List[str]) -> BaseItem:
        self._groups.extend(groups)
        return self

    def remove_group(self, group: str) -> BaseItem:
        if group in self._groups:
            self._groups.remove(group)
        return self

    def config(self) -> BaseItem:
        return self.groups('Config')

    def auto(self) -> BaseItem:
        return self.groups('Auto')

    def location(self, location: Location) -> BaseItem:
        self.location_item(location)
        return self.groups(location.identifier)

    def location_item(self, location: Location) -> BaseItem:
        return self.scripting({'location_item': location.identifier})

    def equipment(self, equipment: Union[str, Equipment]) -> BaseItem:
        if isinstance(equipment, str):
            self.groups(equipment)
        elif isinstance(equipment, Equipment):
            self.groups(equipment.item_ids.equipment_id)

        return self

    def sensor(self,
               measurement: str,
               series_tags: Dict[str, str],
               restore_on_startup: Optional[bool] = False,
               add_item_label: Optional[bool] = False) -> BaseItem:
        if restore_on_startup:
            self.groups('SensorRestore')
        else:
            self.groups('Sensor')

        if add_item_label:
            series_tags['item_label'] = self._label

        self._metadata['influxdb'] = {
            'value': measurement,
            'properties': series_tags
        }

        series_tags['item'] = self._name

        BaseItem.influxdb_series[self._name] = {
            'measurement': measurement,
            'tags': series_tags
        }

        return self

    def remove_sensor(self) -> BaseItem:
        self.remove_group('Sensor')
        self.remove_group('SensorRestore')
        self._metadata.pop('influxdb', None)
        BaseItem.influxdb_series.pop(self._name, None)

        return self

    def aisensor(self, datatype: AISensorDataType) -> BaseItem:
        BaseItem.aisensors[self._name] = str(datatype)
        return self.groups('AISensor')

    def expire(self, duration: str,
               state: Optional[str] = None,
               expire_type: Optional[ExpireType] = None) -> BaseItem:
        value = f'{duration},'

        if state is not None:
            if expire_type is None:
                expire_type = ExpireType.STATE

            value += f'{expire_type}={state}'

        self._metadata['expire'] = {'value': value}
        return self

    def scripting(self, config: Dict[str, str]) -> BaseItem:
        if 'scripting' in self._metadata:
            config = {**self._metadata['scripting']['properties'], **config}

        self._metadata['scripting'] = {'properties': config}
        return self

    def unit(self, unit: str) -> BaseItem:
        self._metadata['unit'] = {'value': unit}
        return self

    def semantic(self,
                 *semantic_tags: List[Union[str, BaseObject, PointType, PropertyType]]) -> BaseItem:
        for tag in semantic_tags:
            if isinstance(tag, str):
                self._tags.append(tag)
            elif isinstance(tag, BaseObject):
                self._tags.append(tag.semantic)
            elif isinstance(tag, PointType) or isinstance(tag, PropertyType):
                self._tags.append(str(tag))

        return self

    def tags(self, *tags: List[str]) -> BaseItem:
        self._tags.extend(tags)
        return self

    def channel(self, channel: str,
                profile_type: Optional[ProfileType] = None,
                profile_properties: Optional[Union[str, Dict]] = None) -> BaseItem:
        self._metadata['channel'] = {'value': channel}
        if not (profile_type is None or profile_properties is None):
            if isinstance(profile_properties, str):
                self._metadata['channel']['properties'] = {
                    'profile': profile_type.profile,
                    profile_type.function: profile_properties
                }
            else:
                self._metadata['channel']['properties'] = {
                    'profile': profile_type.profile,
                    **profile_properties
                }
        return self

    def append_to(self, itemscreator: BaseItemsCreator) -> BaseItem:
        itemscreator.append_item(self)
        return self

    def build_item(self, itemscreator: BaseItemsCreator) -> None:
        itemscreator.append(f'{self.itemtype} {self._name}')

        self._append_label(itemscreator)
        self._append_icon(itemscreator)
        self._append_groups(itemscreator)
        self._append_tags(itemscreator)
        self._append_metadata(itemscreator)

        itemscreator.append('')

    def _append_label(self, itemscreator: BaseItemsCreator) -> None:
        label = Formatter.label(self._label, self._format)

        if label is not None:
            itemscreator.append(f'  "{label.strip()}"')

    def _append_icon(self, itemscreator: BaseItemsCreator) -> None:
        if self._icon is not None:
            itemscreator.append(f'  <{self._icon}>')

    def _append_groups(self, itemscreator: BaseItemsCreator) -> None:
        if len(self._groups) > 0:
            itemscreator.append('  (' + ','.join(self._groups) + ')')

    def _append_tags(self, itemscreator: BaseItemsCreator) -> None:
        if len(self._tags) > 0:
            itemscreator.append('  ["' + '","'.join(self._tags) + '"]')

    def _append_metadata(self, itemscreator: BaseItemsCreator) -> None:
        if len(self._metadata) > 0:
            metatags = {}
            for key, obj in self._metadata.items():
                metadata = ''
                if 'value' in obj:
                    metadata += f'"{obj["value"]}" '
                else:
                    metadata += '"" '

                if 'properties' in obj:
                    metadata += Formatter.key_value_pairs(
                        obj['properties'], '[', ']')

                metatags[key] = metadata.strip()

            itemscreator.append(
                '  ' + Formatter.key_value_pairs(metatags, '{', '}', ",\n   ", False))
