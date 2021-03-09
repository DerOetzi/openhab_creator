from __future__ import annotations

from typing import Dict

from openhab_creator import _, logger
from openhab_creator.models.common import MapTransformation
from openhab_creator.output.basecreator import BaseCreator


class TransformationCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('map', outputdir, 'transform')

    def build(self) -> None:
        self.build_maps()

    def build_maps(self) -> None:
        for map_definition in MapTransformation:
            for key, value in map_definition.mappings.items():
                self.append(f'{key}={value}')

            unknown = _('Unknown')

            if 'NULL' not in map_definition.mappings:
                self.append(f'NULL={unknown}')

            if '-' not in map_definition.mappings:
                self.append(f'-={unknown}')

            if 'UNDEF' not in map_definition.mappings:
                self.append(f'UNDEF={unknown}')

            self.write_file(map_definition.filename)
