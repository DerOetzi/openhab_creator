from __future__ import annotations

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.output.basecreator import BaseCreator


class MapTransformationCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('map', outputdir, 'transform')

    def build(self) -> None:
        self.build_maps()

    def build_maps(self) -> None:
        for map_definition in MapTransformation:
            for key, value in map_definition.mappings.items():
                self.append(f'{key}={value}')

            unknown = _('Unknown')

            if '-' in map_definition.mappings:
                self.append(f'={map_definition.mappings["-"]}')
            else:
                self.append(f'={unknown}')

            self.write_file(map_definition.filename)
