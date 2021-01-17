import os
import shutil
from pathlib import Path


class IconsCreator(object):
    def __init__(self, outputdir: str):
        self._outputdir: str = f'{outputdir}/icons/classic'

    def build(self):
        self.__make_clean_destination_directory()

        pwd = Path(__file__).resolve().parent.parent
        src_dir = f'{pwd}/content/icons'

        for dir in os.scandir(src_dir):
            icon_basename = dir.name
            for file in os.scandir(dir.path):
                if 'default.svg' == file.name:
                    icon_name = f'{icon_basename}.svg'
                elif file.name.endswith('.svg'):
                    icon_name = f'{icon_basename}-{file.name}'
                else:
                    continue

                print(f'Creating {icon_name}')
                destination = os.path.join(self._outputdir, icon_name)
                shutil.copy(file.path, destination)

    def __make_clean_destination_directory(self):
        print('Clean icons directory')
        if os.path.exists(self._outputdir):
            for file in os.scandir(self._outputdir):
                os.remove(file.path)
        else:
            os.makedirs(self._outputdir)
