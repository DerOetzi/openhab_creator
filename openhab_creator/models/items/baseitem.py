from __future__ import annotations

from abc import abstractproperty
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from openhab_creator import CreatorEnum
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.baseobject import BaseObject
from openhab_creator.output.formatter import Formatter

if TYPE_CHECKING:
    from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
    from openhab_creator.models.configuration.location import Location


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
    TIMESTAMP = 'Timestamp'
    ULTRAVIOLET = 'Ultraviolet'
    VIBRATION = 'Vibration'


class BaseItem(object):
    def __init__(self, name: str):
        self._name: str = name
        self._label: str = ''
        self._format: Optional[str] = None
        self._icon: Optional[str] = None
        self._groups: List[str] = []
        self._tags: List[str] = []
        self._metadata: Dict[str, Dict] = {}

    @abstractproperty
    def itemtype(self) -> str:
        pass

    def label(self, label: str) -> BaseItem:
        self._label = label
        return self

    def map(self, mapname: MapTransformation) -> BaseItem:
        return self.format(mapname.formatstr)

    def format(self, format_string: str) -> BaseItem:
        self._format = format_string
        return self

    def icon(self, icon: str) -> BaseItem:
        self._icon = icon.lower()
        return self

    def groups(self, *groups: List[str]) -> BaseItem:
        self._groups.extend(groups)
        return self

    def config(self) -> BaseItem:
        return self.groups('Config')

    def auto(self) -> BaseItem:
        return self.groups('Auto')

    def location(self, location: Location) -> BaseItem:
        return self.groups(location.identifier)

    def sensor(self, measurement: str, series_tags: Dict[str, str]) -> BaseItem:
        self.groups('Sensor')
        self._metadata['influxdb'] = {
            'value': measurement,
            'properties': series_tags
        }

        return self

    def expire(self, duration: str, state: Optional[str] = None) -> BaseItem:
        value = f'{duration},'

        if state is not None:
            value += f'state={state}'

        self._metadata['expire'] = {'value': value}
        return self

    def scripting(self, config: Dict[str, str]) -> BaseItem:
        self._metadata['scripting'] = {'properties': config}
        return self

    def semantic(self, *semantic_tags: List[Union[str, BaseObject, PointType, PropertyType]]) -> BaseItem:
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

    def channel(self, channel: str) -> BaseItem:
        self._metadata['channel'] = {'value': channel}
        return self

    def append_to(self, itemscreator: BaseItemsCreator) -> None:
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
