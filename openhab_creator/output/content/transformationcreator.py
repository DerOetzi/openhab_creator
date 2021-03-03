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

            if 'NULL' not in map_definition.mappings:
                self.append(f'NULL={_("Unknown")}')

            if '-' not in map_definition.mappings:
                self.append(f'-={_("Unknown")}')

            if 'UNDEF' not in map_definition.mappings:
                self.append(f'UNDEF={_("Unknown")}')

            self.write_file(map_definition.filename)