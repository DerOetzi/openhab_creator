from __future__ import annotations
from typing import TYPE_CHECKING

import os
import shutil
from pathlib import Path
from cairosvg import svg2png

if TYPE_CHECKING:
    from posix import DirEntry

from openhab_creator.output.color import Color


class IconsCreator(object):
    def __init__(self, outputdir: str):
        self._outputdir: str = f'{outputdir}/icons/classic'

    def build(self):
        self.__make_clean_destination_directory()

        pwd = Path(__file__).resolve().parent.parent
        src_dir = f'{pwd}/content/icons'

        for category in os.scandir(src_dir):
            icon_basename = category.name
            for srcfile in os.scandir(category.path):
                if 'default.svg' == srcfile.name:
                    icon_name = f'{icon_basename}'
                elif srcfile.name.endswith('.svg'):
                    icon_name = f'{icon_basename}-{srcfile.name}'[0:-4]
                else:
                    continue

                print(f'Create icon: {icon_name}')
                content = self.__generate_output_icons(srcfile)
                self.__write_svg(icon_name, content)
                self.__convert_write_png(icon_name, content)

    def __make_clean_destination_directory(self):
        print('Clean icons directory')
        if os.path.exists(self._outputdir):
            for file in os.scandir(self._outputdir):
                os.remove(file.path)
        else:
            os.makedirs(self._outputdir)

    def __generate_output_icons(self, srcfile: DirEntry) -> str:
        with open(srcfile, 'r') as f:
            content = f.read()
            for color in Color:
                content = content.replace(f'__{color.name}__', color.value)

        return content

    def __write_svg(self, icon_basename: str, content: str) -> None:
        destination = os.path.join(self._outputdir, f'{icon_basename}.svg')
        with open(destination, 'w') as f:
            f.write(content)

    def __convert_write_png(self, icon_basename, content: str) -> None:
        destination = os.path.join(self._outputdir, f'{icon_basename}.png')
        svg2png(bytestring=content, write_to=destination,
                output_height=32, output_width=32)
