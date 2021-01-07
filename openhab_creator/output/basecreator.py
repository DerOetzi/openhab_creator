import os
from typing import List


class BaseCreator(object):
    _outputdir: str
    _type: str
    _check_only: bool

    def __init__(self, typed: str, outputdir: str, check_only: bool = False):
        self._typed = typed
        self._outputdir = f'{outputdir}/{typed}'
        self._check_only = check_only

    def _write_file(self, filename: str, lines: List[str]) -> None:
        if self._check_only:
            return

        self.__create_outputdir_if_not_exists()

        with open(f'{self._outputdir}/{filename}.{self._typed}', 'w') as f:
            f.writelines("\n".join(lines))

    def __create_outputdir_if_not_exists(self) -> None:
        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)
