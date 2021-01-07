import os
from typing import List


class BaseCreator(object):
    _outputdir: str
    _type: str
    _checkOnly: bool

    def __init__(self, typed: str, outputdir: str, checkOnly: bool = False):
        self._typed = typed
        self._outputdir = f'{outputdir}/{typed}'
        self._checkOnly = checkOnly

    def _writeFile(self, filename: str, lines: List[str]) -> None:
        if self._checkOnly:
            return

        self.__createOutputDirIfNotExists()

        with open(f'{self._outputdir}/{filename}.{self._typed}', 'w') as f:
            f.writelines("\n".join(lines))

    def __createOutputDirIfNotExists(self) -> None:
        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)
