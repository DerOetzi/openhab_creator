from __future__ import annotations

from enum import Enum

from openhab_creator import _, logger
from openhab_creator.output.basecreator import BaseCreator


class Maps(Enum):
    lowbattery = {
        '0': _('Ok'),
        '1': _('Low'),
        'OFF': _('Ok'),
        'ON': _('Low')
    }


class TransformationCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('map', outputdir, 'transform')

    def build(self) -> None:
        self.build_maps()

    def build_maps(self) -> None:
        for map_definition in Maps:
            for key, value in map_definition.value.items():
                self.append(f'{key}={value}')

            if 'NULL' not in map_definition.value:
                self.append(f'NULL={_("Unknown")}')

            if '-' not in map_definition.value:
                self.append(f'-={_("Unknown")}')

            if 'UNDEF' not in map_definition.value:
                self.append(f'UNDEF={_("Unknown")}')

            self.write_file(map_definition.name)
