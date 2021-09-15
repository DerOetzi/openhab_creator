from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, List

from cairosvg import svg2png
from openhab_creator import logger
from openhab_creator.output.color import Color
from openhab_creator.output.content.basecontentcreator import \
    BaseContentCreator

if TYPE_CHECKING:
    from posix import DirEntry


class IconsCreator(BaseContentCreator):
    def __init__(self, outputdir: str):
        super().__init__(outputdir)
        self.icons = []

    def build(self, configdir: str) -> None:
        self._create_outputdir_if_not_exists('icons/classic')
        src_dir = Path(configdir) / 'icons'

        for category in os.scandir(src_dir):
            if category.is_dir():
                icon_basename = category.name
                for srcfile in os.scandir(category.path):
                    if srcfile.name == 'default.svg':
                        self._createfiles(srcfile, icon_basename)
                    elif srcfile.name.endswith('.svg'):
                        self._createfiles(
                            srcfile, f'{icon_basename}-{srcfile.name}'[0:-4])
                        self._createfiles(
                            srcfile, f'{icon_basename}{srcfile.name}'[0:-4])
            elif category.name.endswith('.svg'):
                self._createfiles(category, category.name[0:-4])

    def check_icons_exist(self, icons: List[str]) -> None:
        for icon in icons:
            if not icon in self.icons:
                logger.warning('Missing icon: %s', icon)

    def _createfiles(self, srcfile: DirEntry, icon_name: str):
        self.icons.append(icon_name)

        logger.info('Create icon: %s', icon_name)

        content = self.generate_output_icons(srcfile)

        self._write_svg(icon_name, content)
        self._convert_write_png(icon_name, content)

    @staticmethod
    def generate_output_icons(srcpath: DirEntry) -> str:
        with open(srcpath, 'r') as srcfile:
            content = srcfile.read()
            for color in Color:
                content = content.replace(f'__{color.name}__', str(color))

        return content

    def _write_svg(self, icon_basename: str, content: str) -> None:
        destination = self._outputdir / f'icons/classic/{icon_basename}.svg'
        with open(destination, 'w') as destfile:
            destfile.write(content)

    def _convert_write_png(self, icon_basename, content: str) -> None:
        destination = self._outputdir / f'icons/classic/{icon_basename}.png'
        svg2png(bytestring=content, write_to=str(destination),
                output_height=32, output_width=32)
