from __future__ import annotations

import os
from typing import TYPE_CHECKING, List

from openhab_creator.models.configuration import Configuration
from openhab_creator.output.basecreator import BaseCreator
from openhab_creator.output.formatter import Formatter

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.bridge import Bridge
    from openhab_creator.models.configuration.equipment.thing import Channel


class ThingsCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('things', outputdir)

    def build(self, configuration: Configuration) -> None:
        for bridge_key, bridge_obj in configuration.equipment.bridges.items():
            if bridge_obj.is_subbridge:
                continue

            self._append_bridge(bridge_obj)

            if bridge_obj.is_thing:
                self.append('}')
            self.write_file(bridge_key)

    def _append_bridge(self, bridge: Bridge) -> None:
        if bridge.is_thing:
            bridgething = bridge.thing

            bridgestring = f'Bridge {bridge.binding}:{bridgething.typed}:{bridgething.uid} '
            bridgelabel = f'{bridgething.nameprefix} {bridge.name}({bridge.identifier})'.strip(
            )
            bridgestring += f'"{bridgelabel}" '
            if bridgething.has_properties:
                bridgestring += f'{Formatter.key_value_pairs(bridgething.properties, "[", "]")} '

            bridgestring += '{'

            self.append(bridgestring)

        self._append_things(bridge)

    def _append_things(self, bridge: Bridge) -> None:
        for thing in bridge.things:
            thingstring = self._build_thingstring(thing, bridge)

            if thing.has_channels or thing.is_subbridge:
                thingstring += '{'

            self.append(thingstring)

            if thing.has_channels:
                self._append_thing_channels(thing.channels)

            if thing.is_subbridge:
                self._append_things(thing.same_bridge)

            if thing.has_channels or thing.is_subbridge:
                self.append('  }')

    def _build_thingstring(self, thing, bridge):
        thingtype = 'Bridge' if thing.is_subbridge else 'Thing'

        if bridge.is_thing:
            thingstring = f'  {thingtype} {thing.typed} {thing.uid} '
        else:
            thingstring = f'{thingtype} {bridge.binding}:{thing.typed}:{thing.uid} '

        thinglabel = f'{thing.nameprefix} {thing.name} ({thing.identifier})'.strip(
        )

        thingstring += f'"{thinglabel}" '
        thingstring += f'@ "{thing.category}" '

        if thing.has_properties:
            thingstring += f'{Formatter.key_value_pairs(thing.properties, "[", "]")} '
        return thingstring

    def _append_thing_channels(self, channels: List[Channel]) -> None:
        self.append('    Channels:')

        for channel in channels:
            channelstring = f'      Type {channel.typed} : {channel.identifier} "{channel.name}" '
            channelstring += f'{Formatter.key_value_pairs(channel.properties, "[", "]")} '

            self.append(channelstring)
