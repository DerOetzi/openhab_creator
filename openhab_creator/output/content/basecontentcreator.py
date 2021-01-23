from __future__ import annotations
from typing import Optional

from pathlib import Path
import os

import distutils.log
import distutils.dir_util


class BaseContentCreator(object):
    def __init__(self, outputdir: str):
        self._outputdir: str = outputdir

        pwd = Path(__file__).resolve().parent.parent.parent
        self._srcdir: str = f'{pwd}/content/'

    def _copy_all_files_from_subdir(self, subdir: str, destination: Optional[str] = None) -> None:
        if destination is None:
            dest_dir = self._create_outputdir_if_not_exists(subdir)
        else:
            dest_dir = self._create_outputdir_if_not_exists(destination)

        distutils.log.set_verbosity(distutils.log.DEBUG)
        distutils.dir_util.copy_tree(
            f'{self._srcdir}{subdir}',
            dest_dir,
            update=1,
            verbose=1,
        )

    def _create_outputdir_if_not_exists(self, subdir: str) -> str:
        destination = f'{self._outputdir}/{subdir}/'
        if not os.path.exists(destination):
            os.makedirs(destination)

        return destination
