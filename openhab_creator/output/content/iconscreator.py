from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from cairosvg import svg2png
from openhab_creator import logger
from openhab_creator.output.color import Color
from openhab_creator.output.content.basecontentcreator import \
    BaseContentCreator

if TYPE_CHECKING:
    from posix import DirEntry


class IconsCreator(BaseContentCreator):
    def build(self):
        self._create_outputdir_if_not_exists('icons/classic')
        src_dir = Path(self._srcdir) / 'icons'

        for category in os.scandir(src_dir):
            icon_basename = category.name
            for srcfile in os.scandir(category.path):
                if 'default.svg' == srcfile.name:
                    icon_name = f'{icon_basename}'
                    icon_name2 = None
                elif srcfile.name.endswith('.svg'):
                    icon_name = f'{icon_basename}-{srcfile.name}'[0:-4]
                    icon_name2 = f'{icon_basename}{srcfile.name}'[0:-4]
                else:
                    continue

                logger.info('Create icon: %s', icon_name)

                content = self.__generate_output_icons(srcfile)

                self.__write_svg(icon_name, content)
                self.__convert_write_png(icon_name, content)

                if icon_name2 is not None:
                    self.__write_svg(icon_name2, content)
                    self.__convert_write_png(icon_name2, content)

    def __generate_output_icons(self, srcfile: DirEntry) -> str:
        with open(srcfile, 'r') as f:
            content = f.read()
            for color in Color:
                content = content.replace(f'__{color.name}__', str(color))

        return content

    def __write_svg(self, icon_basename: str, content: str) -> None:
        destination = self._outputdir / f'icons/classic/{icon_basename}.svg'
        with open(destination, 'w') as f:
            f.write(content)

    def __convert_write_png(self, icon_basename, content: str) -> None:
        destination = self._outputdir / f'icons/classic/{icon_basename}.png'
        svg2png(bytestring=content, write_to=str(destination),
                output_height=32, output_width=32)
