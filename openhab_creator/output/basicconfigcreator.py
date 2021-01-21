from __future__ import annotations
from typing import TYPE_CHECKING

import os
from pathlib import Path
import shutil


class BasicConfigCreator(object):
    def __init__(self, outputdir: str):
        self._outputdir = outputdir

        pwd = Path(__file__).resolve().parent.parent
        self._srcdir = f'{pwd}/content/'

    def build(self) -> None:
        self._copy_services()
        self._copy_persistence()

    def _copy_services(self) -> None:
        self._copy_all_files_from_subdir('services')

    def _copy_persistence(self) -> None:
        self._copy_all_files_from_subdir('persistence')

    def _copy_all_files_from_subdir(self, subdir: str) -> None:
        destination = self.__create_outputdir_if_not_exists(subdir)
        for cfgfile in os.scandir(f'{self._srcdir}/{subdir}'):
            filename = os.path.basename(cfgfile)
            print(f'Copy basic configuration file: {subdir}/{filename}')
            shutil.copy(cfgfile, os.path.join(destination, filename))

    def __create_outputdir_if_not_exists(self, subdir: str) -> str:
        destination = f'{self._outputdir}/{subdir}/'
        if not os.path.exists(destination):
            os.makedirs(destination)

        return destination
